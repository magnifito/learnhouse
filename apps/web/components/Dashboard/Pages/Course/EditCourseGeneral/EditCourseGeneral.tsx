import FormLayout, {
  FormField,
  FormLabelAndMessage,
  Input,
  Textarea,
} from '@components/Objects/StyledElements/Form/Form';
import { useFormik } from 'formik';
import { AlertTriangle } from 'lucide-react';
import * as Form from '@radix-ui/react-form';
import React, { useEffect, useState } from 'react';
import ThumbnailUpdate from './ThumbnailUpdate';
import { useCourse, useCourseDispatch } from '@components/Contexts/CourseContext';
import FormTagInput from '@components/Objects/StyledElements/Form/TagInput';
import LearningItemsList from './LearningItemsList';
import {
  CustomSelect,
  CustomSelectContent,
  CustomSelectItem,
  CustomSelectTrigger,
  CustomSelectValue,
} from "./CustomSelect";
import { useTranslations } from 'next-intl';

type EditCourseStructureProps = {
  orgslug: string
  course_uuid?: string
}

const validate = (values: any, t: any) => {
  const errors = {} as any;

  if (!values.name) {
    errors.name = t('required');
  } else if (values.name.length > 100) {
    errors.name = t('maxLength', { count: 100 });
  }

  if (!values.description) {
    errors.description = t('required');
  } else if (values.description.length > 1000) {
    errors.description = t('maxLength', { count: 1000 });
  }

  if (!values.learnings) {
    errors.learnings = t('required');
  } else {
    try {
      const learningItems = JSON.parse(values.learnings);
      if (!Array.isArray(learningItems)) {
        errors.learnings = t('invalidFormat');
      } else if (learningItems.length === 0) {
        errors.learnings = t('learningsRequired');
      } else {
        // Check if any item has empty text
        const hasEmptyText = learningItems.some((item: any) => !item.text || item.text.trim() === '');
        if (hasEmptyText) {
          errors.learnings = t('learningsEmptyText');
        }
      }
    } catch (e) {
      errors.learnings = t('invalidFormat');
    }
  }

  return errors;
};

function EditCourseGeneral(props: EditCourseStructureProps) {
  const t = useTranslations('courseEditor');
  const [error, setError] = useState('');
  const course = useCourse();
  const dispatchCourse = useCourseDispatch() as any;
  const { isLoading, courseStructure } = course as any;

  // Initialize learnings as a JSON array if it's not already
  const initializeLearnings = (learnings: any) => {
    if (!learnings) {
      return JSON.stringify([{ id: Date.now().toString(), text: '', emoji: '📝' }]);
    }

    try {
      // Check if it's already a valid JSON array
      const parsed = JSON.parse(learnings);
      if (Array.isArray(parsed)) {
        return learnings;
      }

      // If it's a string but not a JSON array, convert it to a learning item
      if (typeof learnings === 'string') {
        return JSON.stringify([{
          id: Date.now().toString(),
          text: learnings,
          emoji: '📝'
        }]);
      }

      // Default empty array
      return JSON.stringify([{ id: Date.now().toString(), text: '', emoji: '📝' }]);
    } catch (e) {
      // If it's not valid JSON, convert the string to a learning item
      if (typeof learnings === 'string') {
        return JSON.stringify([{
          id: Date.now().toString(),
          text: learnings,
          emoji: '📝'
        }]);
      }

      // Default empty array
      return JSON.stringify([{ id: Date.now().toString(), text: '', emoji: '📝' }]);
    }
  };

  // Create initial values object
  const getInitialValues = () => {
    const thumbnailType = courseStructure?.thumbnail_type || 'image';
    return {
      name: courseStructure?.name || '',
      description: courseStructure?.description || '',
      about: courseStructure?.about || '',
      learnings: initializeLearnings(courseStructure?.learnings || ''),
      tags: courseStructure?.tags || '',
      public: courseStructure?.public || false,
      thumbnail_type: thumbnailType,
    };
  };

  const formik = useFormik({
    initialValues: getInitialValues(),
    validate: (values: any) => validate(values, t),
    onSubmit: async values => {
      try {
        // Add your submission logic here
        dispatchCourse({ type: 'setIsSaved' });
      } catch (e) {
        setError(t('saveError'));
      }
    },
    enableReinitialize: true,
  }) as any;

  // Reset form when courseStructure changes
  useEffect(() => {
    if (courseStructure && !isLoading) {
      const newValues = getInitialValues();
      formik.resetForm({ values: newValues });
    }
  }, [courseStructure, isLoading]);

  useEffect(() => {
    if (!isLoading) {
      const formikValues = formik.values as any;
      const initialValues = formik.initialValues as any;
      const valuesChanged = Object.keys(formikValues).some(
        key => formikValues[key] !== initialValues[key]
      );

      if (valuesChanged) {
        dispatchCourse({ type: 'setIsNotSaved' });
        const updatedCourse = {
          ...courseStructure,
          ...formikValues,
        };
        dispatchCourse({ type: 'setCourseStructure', payload: updatedCourse });
      }
    }
  }, [formik.values, isLoading]);

  if (isLoading || !courseStructure) {
    return <div>Loading...</div>;
  }

  return (
    <div className="h-full">
      <div className="h-6" />
      <div className="px-10 pb-10">
        <div className="bg-white rounded-xl shadow-xs">
          <FormLayout onSubmit={formik.handleSubmit} className="p-6">
            {error && (
              <div className="flex justify-center bg-red-200 rounded-md text-red-950 space-x-2 items-center p-4 mb-6 transition-all shadow-xs">
                <AlertTriangle size={18} />
                <div className="font-bold text-sm">{error}</div>
              </div>
            )}

            <div className="space-y-6">
              <FormField name="name">
                <FormLabelAndMessage label={t('name')} message={formik.errors.name} />
                <Form.Control asChild>
                  <Input
                    style={{ backgroundColor: 'white' }}
                    onChange={formik.handleChange}
                    value={formik.values.name}
                    type="text"
                    required
                  />
                </Form.Control>
              </FormField>

              <FormField name="description">
                <FormLabelAndMessage label={t('description')} message={formik.errors.description} />
                <Form.Control asChild>
                  <Input
                    style={{ backgroundColor: 'white' }}
                    onChange={formik.handleChange}
                    value={formik.values.description}
                    type="text"
                    required
                  />
                </Form.Control>
              </FormField>

              <FormField name="about">
                <FormLabelAndMessage label={t('about')} message={formik.errors.about} />
                <Form.Control asChild>
                  <Textarea
                    style={{ backgroundColor: 'white', height: '200px', minHeight: '200px' }}
                    onChange={formik.handleChange}
                    value={formik.values.about}
                    required
                  />
                </Form.Control>
              </FormField>

              <FormField name="learnings">
                <FormLabelAndMessage label={t('learnings')} message={formik.errors.learnings} />
                <Form.Control asChild>
                  <LearningItemsList
                    value={formik.values.learnings}
                    onChange={(value) => formik.setFieldValue('learnings', value)}
                    error={formik.errors.learnings}
                  />
                </Form.Control>
              </FormField>

              <FormField name="tags">
                <FormLabelAndMessage label={t('tags')} message={formik.errors.tags} />
                <Form.Control asChild>
                  <FormTagInput
                    placeholder={t('enterToAdd')}
                    onChange={(value) => formik.setFieldValue('tags', value)}
                    value={formik.values.tags}
                  />
                </Form.Control>
              </FormField>

              <FormField name="thumbnail_type">
                <FormLabelAndMessage label={t('thumbnailType')} />
                <Form.Control asChild>
                  <CustomSelect
                    value={formik.values.thumbnail_type}
                    onValueChange={(value) => {
                      if (!value) return;
                      formik.setFieldValue('thumbnail_type', value);
                    }}
                  >
                    <CustomSelectTrigger className="w-full bg-white">
                      <CustomSelectValue>
                        {formik.values.thumbnail_type === 'image' ? t('image') :
                          formik.values.thumbnail_type === 'video' ? t('video') :
                            formik.values.thumbnail_type === 'both' ? t('both') : t('image')}
                      </CustomSelectValue>
                    </CustomSelectTrigger>
                    <CustomSelectContent>
                      <CustomSelectItem value="image">{t('image')}</CustomSelectItem>
                      <CustomSelectItem value="video">{t('video')}</CustomSelectItem>
                      <CustomSelectItem value="both">{t('both')}</CustomSelectItem>
                    </CustomSelectContent>
                  </CustomSelect>
                </Form.Control>
              </FormField>

              <FormField name="thumbnail">
                <FormLabelAndMessage label={t('thumbnail')} />
                <Form.Control asChild>
                  <ThumbnailUpdate thumbnailType={formik.values.thumbnail_type} />
                </Form.Control>
              </FormField>
            </div>
          </FormLayout>
        </div>
      </div>
    </div>
  );
}

export default EditCourseGeneral;
