import FormLayout, {
  ButtonBlack,
  Flex,
  FormField,
  FormLabel,
  FormMessage,
  Input,
} from '@components/Objects/StyledElements/Form/Form'
import React, { useState } from 'react'
import * as Form from '@radix-ui/react-form'
import { useTranslations } from 'next-intl';
import BarLoader from 'react-spinners/BarLoader'
import { constructAcceptValue } from '@/lib/constants';

const SUPPORTED_FILES = constructAcceptValue(['pdf'])

function DocumentPdfModal({ submitFileActivity, chapterId, course }: any) {
  const t = useTranslations('activityModals');
  const [documentpdf, setDocumentPdf] = React.useState(null) as any
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [name, setName] = React.useState('')

  const handleDocumentPdfChange = (event: React.ChangeEvent<any>) => {
    setDocumentPdf(event.target.files[0])
  }

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setName(event.target.value)
  }

  const handleSubmit = async (e: any) => {
    e.preventDefault()
    setIsSubmitting(true)
    let status = await submitFileActivity(
      documentpdf,
      'documentpdf',
      {
        name: name,
        chapter_id: chapterId,
        activity_type: 'TYPE_DOCUMENT',
        activity_sub_type: 'SUBTYPE_DOCUMENT_PDF',
        published_version: 1,
        version: 1,
        course_id: course.id,
      },
      chapterId
    )
    setIsSubmitting(false)
  }

  return (
    <FormLayout onSubmit={handleSubmit}>
      <FormField name="documentpdf-activity-name">
        <Flex css={{ alignItems: 'baseline', justifyContent: 'space-between' }}>
          <FormLabel>{t('document.name')}</FormLabel>
          <FormMessage match="valueMissing">
            {t('document.namePlaceholder')}
          </FormMessage>
        </Flex>
        <Form.Control asChild>
          <Input onChange={handleNameChange} type="text" required />
        </Form.Control>
      </FormField>
      <FormField name="documentpdf-activity-file">
        <Flex css={{ alignItems: 'baseline', justifyContent: 'space-between' }}>
          <FormLabel>{t('document.fileLabel')}</FormLabel>
          <FormMessage match="valueMissing">
            {t('document.fileError')}
          </FormMessage>
        </Flex>
        <Form.Control asChild>
          <input accept={SUPPORTED_FILES} type="file" onChange={handleDocumentPdfChange} required />
        </Form.Control>
      </FormField>

      <Flex css={{ marginTop: 25, justifyContent: 'flex-end' }}>
        <Form.Submit asChild>
          <ButtonBlack type="submit" css={{ marginTop: 10 }}>
            {isSubmitting ? (
              <BarLoader
                cssOverride={{ borderRadius: 60 }}
                width={60}
                color="#ffffff"
              />
            ) : (
              t('common.create')
            )}
          </ButtonBlack>
        </Form.Submit>
      </Flex>
    </FormLayout>
  )
}

export default DocumentPdfModal
