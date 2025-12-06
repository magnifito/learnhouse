'use client'
import React from 'react'
import { LandingObject, LandingSection, LandingHeroSection, LandingTextAndImageSection, LandingLogos, LandingPeople, LandingBackground, LandingButton, LandingImage, LandingFeaturedCourses } from './landing_types'
import { Plus, Trash2, GripVertical, LayoutTemplate, ImageIcon, Users, Award, Edit, Link, Upload, Save, BookOpen, TextIcon } from 'lucide-react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import { Input } from "@components/ui/input"
import { Textarea } from "@components/ui/textarea"
import { Label } from "@components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@components/ui/select"
import { Button } from "@components/ui/button"
import { useOrg } from '@components/Contexts/OrgContext'
import { useLHSession } from '@components/Contexts/LHSessionContext'
import { updateOrgLanding, uploadLandingContent } from '@services/organizations/orgs'
import { getOrgLandingMediaDirectory } from '@services/media/media'
import { getOrgCourses } from '@services/courses/courses'
import toast from 'react-hot-toast'
import useSWR from 'swr'
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@components/ui/tabs"

import { useTranslations } from 'next-intl'

const SECTION_TYPES = {
  hero: {
    icon: LayoutTemplate,
    labelKey: 'heroLabel',
    descriptionKey: 'heroDescription'
  },
  'text-and-image': {
    icon: ImageIcon,
    labelKey: 'textImageLabel',
    descriptionKey: 'textImageDescription'
  },
  logos: {
    icon: Award,
    labelKey: 'logosLabel',
    descriptionKey: 'logosDescription'
  },
  people: {
    icon: Users,
    labelKey: 'peopleLabel',
    descriptionKey: 'peopleDescription'
  },
  'featured-courses': {
    icon: BookOpen,
    labelKey: 'coursesLabel',
    descriptionKey: 'coursesDescription'
  }
} as const

const PREDEFINED_GRADIENTS = {
  'sunrise': {
    colors: ['#fef9f3', '#ffecd2'] as Array<string>,
    direction: '45deg'
  },
  'mint-breeze': {
    colors: ['#f0fff4', '#dcfce7'] as Array<string>,
    direction: '45deg'
  },
  'deep-ocean': {
    colors: ['#0f172a', '#1e3a8a'] as Array<string>,
    direction: '135deg'
  },
  'sunset-blaze': {
    colors: ['#7f1d1d', '#ea580c'] as Array<string>,
    direction: '45deg'
  },
  'midnight-purple': {
    colors: ['#581c87', '#7e22ce'] as Array<string>,
    direction: '90deg'
  },
  'forest-depths': {
    colors: ['#064e3b', '#059669'] as Array<string>,
    direction: '225deg'
  },
  'berry-fusion': {
    colors: ['#831843', '#be185d'] as Array<string>,
    direction: '135deg'
  },
  'cosmic-night': {
    colors: ['#1e1b4b', '#4338ca'] as Array<string>,
    direction: '45deg'
  },
  'autumn-fire': {
    colors: ['#7c2d12', '#c2410c'] as Array<string>,
    direction: '90deg'
  },
  'emerald-depths': {
    colors: ['#064e3b', '#10b981'] as Array<string>,
    direction: '135deg'
  },
  'royal-navy': {
    colors: ['#1e3a8a', '#3b82f6'] as Array<string>,
    direction: '225deg'
  },
  'volcanic': {
    colors: ['#991b1b', '#f97316'] as Array<string>,
    direction: '315deg'
  },
  'arctic-night': {
    colors: ['#0f172a', '#475569'] as Array<string>,
    direction: '90deg'
  },
  'grape-punch': {
    colors: ['#6b21a8', '#d946ef'] as Array<string>,
    direction: '135deg'
  },
  'marine-blue': {
    colors: ['#0c4a6e', '#0ea5e9'] as Array<string>,
    direction: '45deg'
  }
} as const

const GRADIENT_DIRECTIONS = {
  '45deg': '↗️ Top Right',
  '90deg': '⬆️ Top',
  '135deg': '↖️ Top Left',
  '180deg': '⬅️ Left',
  '225deg': '↙️ Bottom Left',
  '270deg': '⬇️ Bottom',
  '315deg': '↘️ Bottom Right',
  '0deg': '➡️ Right'
} as const

const getSectionDisplayName = (section: LandingSection, t: any) => {
  const sectionType = SECTION_TYPES[section.type as keyof typeof SECTION_TYPES]
  return t(sectionType.labelKey)
}

const OrgEditLanding = () => {
  const t = useTranslations()
  const org = useOrg() as any
  const session = useLHSession() as any
  const access_token = session?.data?.tokens?.access_token
  const [isLandingEnabled, setIsLandingEnabled] = React.useState(false)
  const [landingData, setLandingData] = React.useState<LandingObject>({
    sections: [],
    enabled: false
  })
  const [selectedSection, setSelectedSection] = React.useState<number | null>(null)
  const [isSaving, setIsSaving] = React.useState(false)

  // Initialize landing data from org config
  React.useEffect(() => {
    if (org?.config?.config?.landing) {
      const landingConfig = org.config.config.landing
      setLandingData({
        sections: landingConfig.sections || [],
        enabled: landingConfig.enabled || false
      })
      setIsLandingEnabled(landingConfig.enabled || false)
    }
  }, [org])

  const addSection = (type: string) => {
    const newSection: LandingSection = createEmptySection(type)
    setLandingData(prev => ({
      ...prev,
      sections: [...prev.sections, newSection]
    }))
  }

  const createEmptySection = (type: string): LandingSection => {
    switch (type) {
      case 'hero':
        return {
          type: 'hero',
          title: 'New Hero Section',
          background: {
            type: 'solid',
            color: '#ffffff'
          },
          heading: {
            text: 'Welcome',
            color: '#000000',
            size: 'large'
          },
          subheading: {
            text: 'Start your learning journey',
            color: '#666666',
            size: 'medium'
          },
          buttons: [],
          illustration: undefined,
          contentAlign: 'center'
        }
      case 'text-and-image':
        return {
          type: 'text-and-image',
          title: 'New Text & Image Section',
          text: 'Add your content here',
          flow: 'left',
          image: {
            url: '',
            alt: ''
          },
          buttons: []
        }
      case 'logos':
        return {
          type: 'logos',
          title: 'New Logos Section',
          logos: []
        }
      case 'people':
        return {
          type: 'people',
          title: 'New People Section',
          people: []
        }
      case 'featured-courses':
        return {
          type: 'featured-courses',
          title: 'Courses',
          courses: []
        }
      default:
        throw new Error('Invalid section type')
    }
  }

  const updateSection = (index: number, updatedSection: LandingSection) => {
    const newSections = [...landingData.sections]
    newSections[index] = updatedSection
    setLandingData(prev => ({
      ...prev,
      sections: newSections
    }))
  }

  const deleteSection = (index: number) => {
    setLandingData(prev => ({
      ...prev,
      sections: prev.sections.filter((_, i) => i !== index)
    }))
    setSelectedSection(null)
  }

  const onDragEnd = (result: any) => {
    if (!result.destination) return

    const items = Array.from(landingData.sections)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)

    setLandingData(prev => ({
      ...prev,
      sections: items
    }))
    setSelectedSection(result.destination.index)
  }

  const handleSave = async () => {
    if (!org?.id) {
      toast.error(t('landing.orgIdNotFound'))
      return
    }

    setIsSaving(true)
    try {
      const res = await updateOrgLanding(org.id, {
        sections: landingData.sections,
        enabled: isLandingEnabled
      }, access_token)

      if (res.status === 200) {
        toast.success(t('landing.landingPageSaved'))
      } else {
        toast.error(t('landing.errorSavingLanding'))
      }
    } catch (error) {
      toast.error(t('landing.errorSavingLanding'))
      console.error('Error saving landing page:', error)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="sm:mx-10 mx-0 bg-white rounded-xl nice-shadow">
      <div className="p-6 space-y-6">
        {/* Enable/Disable Landing Page */}
        <div className="flex items-center justify-between border-b pb-4">
          <div>
            <h2 className="text-xl font-semibold flex items-center">{t('landing.landingPage')} <div className="text-xs ml-2 bg-gray-200 text-gray-700 px-2 py-1 rounded-full"> {t('landing.beta')} </div></h2>
            <p className="text-gray-600">{t('landing.customizeLanding')}</p>
          </div>
          <div className="flex items-center space-x-4">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={isLandingEnabled}
                onChange={() => setIsLandingEnabled(!isLandingEnabled)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-hidden peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
            <Button
              variant="default"
              onClick={handleSave}
              disabled={isSaving}
              className="bg-black hover:bg-black/90"
            >
              <Save className="h-4 w-4 mr-2" />
              {isSaving ? t('landing.savingChanges') : t('landing.saveChanges')}
            </Button>
          </div>
        </div>

        {isLandingEnabled && (
          <>
            {/* Section List */}
            <div className="grid grid-cols-4 gap-6">
              {/* Sections Panel */}
              <div className="col-span-1 border-r pr-4">
                <h3 className="font-medium mb-4">{t('landing.sections')}</h3>
                <DragDropContext onDragEnd={onDragEnd}>
                  <Droppable droppableId="sections">
                    {(provided) => (
                      <div
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        className="space-y-2"
                      >
                        {landingData.sections.map((section, index) => (
                          <Draggable
                            key={`section-${index}`}
                            draggableId={`section-${index}`}
                            index={index}
                          >
                            {(provided, snapshot) => (
                              <div
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                onClick={() => setSelectedSection(index)}
                                className={`p-4 bg-white/80 backdrop-blur-xs rounded-lg cursor-pointer border  ${selectedSection === index
                                  ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500/20 shadow-xs'
                                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50/50 hover:shadow-xs'
                                  } ${snapshot.isDragging ? 'shadow-lg ring-2 ring-blue-500/20 rotate-2' : ''}`}
                              >
                                <div className="flex items-center justify-between group">
                                  <div className="flex items-center space-x-3">
                                    <div {...provided.dragHandleProps}
                                      className={`p-1.5 rounded-md transition-colors duration-200 ${selectedSection === index
                                        ? 'text-blue-500 bg-blue-100/50'
                                        : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                                        }`}>
                                      <GripVertical size={16} />
                                    </div>
                                    <div className={`p-1.5 rounded-md ${selectedSection === index
                                      ? 'text-blue-600 bg-blue-100/50'
                                      : 'text-gray-600 bg-gray-100/50'
                                      }`}>
                                      {React.createElement(SECTION_TYPES[section.type as keyof typeof SECTION_TYPES].icon, {
                                        size: 16
                                      })}
                                    </div>
                                    <span className={`text-sm font-medium truncate capitalize ${selectedSection === index
                                      ? 'text-blue-700'
                                      : 'text-gray-700'
                                      }`}>
                                      {getSectionDisplayName(section, t)}
                                    </span>
                                  </div>
                                  <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        setSelectedSection(index)
                                      }}
                                      className={`p-1.5 rounded-md transition-colors duration-200 ${selectedSection === index
                                        ? 'text-blue-500 hover:bg-blue-100'
                                        : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                                        }`}
                                    >
                                      <Edit size={14} />
                                    </button>
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        deleteSection(index)
                                      }}
                                      className="p-1.5 text-red-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors duration-200"
                                    >
                                      <Trash2 size={14} />
                                    </button>
                                  </div>
                                </div>
                              </div>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </DragDropContext>

                <div className="pt-4">
                  <Select
                    onValueChange={(value) => {
                      if (value) {
                        addSection(value)
                      }
                    }}
                  >
                    <SelectTrigger className="w-full p-0 border-0 bg-black ">
                      <div className="w-full">
                        <Button variant="default" className="w-full bg-black hover:bg-black/90 text-white">
                          <Plus className="h-4 w-4 mr-2" />
                          {t('landing.addSection')}
                        </Button>
                      </div>
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(SECTION_TYPES).map(([type, { icon: Icon, labelKey, descriptionKey }]) => (
                        <SelectItem key={type} value={type}>
                          <div className="flex items-center space-x-3 py-1">
                            <div className="p-1.5 bg-gray-50 rounded-md">
                              <Icon size={16} className="text-gray-600" />
                            </div>
                            <div className="flex-1">
                              <div className="font-medium text-sm text-gray-700">{t(labelKey)}</div>
                              <div className="text-xs text-gray-500">{t(descriptionKey)}</div>
                            </div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Editor Panel */}
              <div className="col-span-3">
                {selectedSection !== null ? (
                  <SectionEditor
                    section={landingData.sections[selectedSection]}
                    onChange={(updatedSection) => updateSection(selectedSection, updatedSection)}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-500">
                    {t('landing.selectToEdit')}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

interface SectionEditorProps {
  section: LandingSection
  onChange: (section: LandingSection) => void
}

const SectionEditor: React.FC<SectionEditorProps> = ({ section, onChange }) => {
  switch (section.type) {
    case 'hero':
      return <HeroSectionEditor section={section} onChange={onChange} />
    case 'text-and-image':
      return <TextAndImageSectionEditor section={section} onChange={onChange} />
    case 'logos':
      return <LogosSectionEditor section={section} onChange={onChange} />
    case 'people':
      return <PeopleSectionEditor section={section} onChange={onChange} />
    case 'featured-courses':
      return <FeaturedCoursesEditor section={section} onChange={onChange} />
    default:
      return <div>Unknown section type</div>
  }
}

const HeroSectionEditor: React.FC<{
  section: LandingHeroSection
  onChange: (section: LandingHeroSection) => void
}> = ({ section, onChange }) => {

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        onChange({
          ...section,
          background: {
            type: 'image',
            image: reader.result as string
          }
        })
      }
      reader.readAsDataURL(file)
    }
  }

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg nice-shadow">
      <div className="flex items-center space-x-2">
        <LayoutTemplate className="w-5 h-5 text-gray-500" />
        <h3 className="font-medium text-lg">{t('landing.heroSection')}</h3>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <Label htmlFor="title">{t('landing.sectionTitle')}</Label>
          <Input
            id="title"
            value={section.title}
            onChange={(e) => onChange({ ...section, title: e.target.value })}
            placeholder={t('landing.enterSectionTitle')}
          />
        </div>

        <Tabs defaultValue="content" className="w-full">
          <TabsList className="grid w-full grid-cols-4 p-1 bg-gray-100 rounded-lg">
            <TabsTrigger value="content" className="flex items-center space-x-2">
              <TextIcon className="h-4 w-4" />
              <span>{t('landing.tabs.content')}</span>
            </TabsTrigger>
            <TabsTrigger value="background" className="flex items-center space-x-2">
              <LayoutTemplate className="h-4 w-4" />
              <span>{t('landing.tabs.background')}</span>
            </TabsTrigger>
            <TabsTrigger value="buttons" className="flex items-center space-x-2">
              <Button className="h-4 w-4" />
              <span>{t('landing.tabs.buttons')}</span>
            </TabsTrigger>
            <TabsTrigger value="illustration" className="flex items-center space-x-2">
              <ImageIcon className="h-4 w-4" />
              <span>{t('landing.tabs.illustration')}</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="content" className="space-y-4 mt-4">
            {/* Heading */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="heading">{t('landing.heading.label')}</Label>
                <Input
                  id="heading"
                  value={section.heading.text}
                  onChange={(e) => onChange({
                    ...section,
                    heading: { ...section.heading, text: e.target.value }
                  })}
                  placeholder={t('landing.heading.placeholder')}
                />
              </div>
              <div>
                <Label htmlFor="headingColor">{t('landing.heading.color')}</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="headingColor"
                    type="color"
                    value={section.heading.color}
                    onChange={(e) => onChange({
                      ...section,
                      heading: { ...section.heading, color: e.target.value }
                    })}
                    className="w-20 h-10 p-1"
                  />
                  <Input
                    value={section.heading.color}
                    onChange={(e) => onChange({
                      ...section,
                      heading: { ...section.heading, color: e.target.value }
                    })}
                    placeholder="#000000"
                    className="font-mono"
                  />
                </div>
              </div>
            </div>

            {/* Subheading */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="subheading">{t('landing.subheading.label')}</Label>
                <Input
                  id="subheading"
                  value={section.subheading.text}
                  onChange={(e) => onChange({
                    ...section,
                    subheading: { ...section.subheading, text: e.target.value }
                  })}
                  placeholder={t('landing.subheading.placeholder')}
                />
              </div>
              <div>
                <Label htmlFor="subheadingColor">{t('landing.subheading.color')}</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="subheadingColor"
                    type="color"
                    value={section.subheading.color}
                    onChange={(e) => onChange({
                      ...section,
                      subheading: { ...section.subheading, color: e.target.value }
                    })}
                    className="w-20 h-10 p-1"
                  />
                  <Input
                    value={section.subheading.color}
                    onChange={(e) => onChange({
                      ...section,
                      subheading: { ...section.subheading, color: e.target.value }
                    })}
                    placeholder="#666666"
                    className="font-mono"
                  />
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="background" className="space-y-4 mt-4">
            <div>
              <Label htmlFor="background">{t('landing.background.type')}</Label>
              <Select
                value={section.background.type}
                onValueChange={(value) => {
                  onChange({
                    ...section,
                    background: {
                      type: value as LandingBackground['type'],
                      color: value === 'solid' ? '#ffffff' : undefined,
                      colors: value === 'gradient' ? PREDEFINED_GRADIENTS['sunrise'].colors : undefined,
                      image: value === 'image' ? '' : undefined
                    }
                  })
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('landing.background.selectType')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="solid">{t('landing.background.types.solid')}</SelectItem>
                  <SelectItem value="gradient">{t('landing.background.types.gradient')}</SelectItem>
                  <SelectItem value="image">{t('landing.background.types.image')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {section.background.type === 'solid' && (
              <div>
                <Label htmlFor="backgroundColor">{t('landing.background.color')}</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="backgroundColor"
                    type="color"
                    value={section.background.color || '#ffffff'}
                    onChange={(e) => onChange({
                      ...section,
                      background: { ...section.background, color: e.target.value }
                    })}
                    className="w-20 h-10 p-1"
                  />
                  <Input
                    value={section.background.color || '#ffffff'}
                    onChange={(e) => onChange({
                      ...section,
                      background: { ...section.background, color: e.target.value }
                    })}
                    placeholder="#ffffff"
                    className="font-mono"
                  />
                </div>
              </div>
            )}

            {section.background.type === 'gradient' && (
              <div className="space-y-4">
                <div>
                  <Label>{t('landing.background.gradient.type')}</Label>
                  <Select
                    value={Object.values(PREDEFINED_GRADIENTS).some(
                      preset => preset.colors[0] === section.background.colors?.[0] &&
                        preset.colors[1] === section.background.colors?.[1]
                    ) ? 'preset' : 'custom'}
                    onValueChange={(value) => {
                      if (value === 'custom') {
                        onChange({
                          ...section,
                          background: {
                            type: 'gradient',
                            colors: ['#ffffff', '#f0f0f0'],
                            direction: section.background.direction || '45deg'
                          }
                        })
                      } else {
                        onChange({
                          ...section,
                          background: {
                            type: 'gradient',
                            colors: PREDEFINED_GRADIENTS['sunrise'].colors,
                            direction: PREDEFINED_GRADIENTS['sunrise'].direction
                          }
                        })
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('landing.background.gradient.selectType')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="preset">{t('landing.background.gradient.preset')}</SelectItem>
                      <SelectItem value="custom">{t('landing.background.gradient.custom')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {!Object.values(PREDEFINED_GRADIENTS).some(
                  preset => preset.colors[0] === section.background.colors?.[0] &&
                    preset.colors[1] === section.background.colors?.[1]
                ) ? (
                  <div className="space-y-4">
                    <div>
                      <Label>{t('landing.background.gradient.startColor')}</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          type="color"
                          value={section.background.colors?.[0] || '#ffffff'}
                          onChange={(e) => onChange({
                            ...section,
                            background: {
                              ...section.background,
                              colors: [e.target.value, section.background.colors?.[1] || '#f0f0f0']
                            }
                          })}
                          className="w-20 h-10 p-1"
                        />
                        <Input
                          value={section.background.colors?.[0] || '#ffffff'}
                          onChange={(e) => onChange({
                            ...section,
                            background: {
                              ...section.background,
                              colors: [e.target.value, section.background.colors?.[1] || '#f0f0f0']
                            }
                          })}
                          placeholder="#ffffff"
                          className="font-mono"
                        />
                      </div>
                    </div>

                    <div>
                      <Label>{t('landing.background.gradient.endColor')}</Label>
                      <div className="flex items-center space-x-2">
                        <Input
                          type="color"
                          value={section.background.colors?.[1] || '#f0f0f0'}
                          onChange={(e) => onChange({
                            ...section,
                            background: {
                              ...section.background,
                              colors: [section.background.colors?.[0] || '#ffffff', e.target.value]
                            }
                          })}
                          className="w-20 h-10 p-1"
                        />
                        <Input
                          value={section.background.colors?.[1] || '#f0f0f0'}
                          onChange={(e) => onChange({
                            ...section,
                            background: {
                              ...section.background,
                              colors: [section.background.colors?.[0] || '#ffffff', e.target.value]
                            }
                          })}
                          placeholder="#f0f0f0"
                          className="font-mono"
                        />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div>
                    <Label>{t('landing.background.gradient.presetLabel')}</Label>
                    <Select
                      value={Object.entries(PREDEFINED_GRADIENTS).find(
                        ([_, gradient]) =>
                          gradient.colors[0] === section.background.colors?.[0] &&
                          gradient.colors[1] === section.background.colors?.[1]
                      )?.[0] || 'sunrise'}
                      onValueChange={(value) => onChange({
                        ...section,
                        background: {
                          ...section.background,
                          colors: PREDEFINED_GRADIENTS[value as keyof typeof PREDEFINED_GRADIENTS].colors,
                          direction: PREDEFINED_GRADIENTS[value as keyof typeof PREDEFINED_GRADIENTS].direction
                        }
                      })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={t('landing.background.gradient.selectPreset')} />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(PREDEFINED_GRADIENTS).map(([name]) => (
                          <SelectItem key={name} value={name}>
                            <div className="flex items-center space-x-2">
                              <div
                                className="w-8 h-8 rounded-md"
                                style={{
                                  background: `linear-gradient(${PREDEFINED_GRADIENTS[name as keyof typeof PREDEFINED_GRADIENTS].direction}, ${PREDEFINED_GRADIENTS[name as keyof typeof PREDEFINED_GRADIENTS].colors.join(', ')})`
                                }}
                              />
                              <span className="capitalize">{name.replace('-', ' ')}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <div>
                  <Label>{t('landing.background.gradient.direction')}</Label>
                  <Select
                    value={section.background.direction || '45deg'}
                    onValueChange={(value) => onChange({
                      ...section,
                      background: { ...section.background, direction: value }
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('landing.background.gradient.selectDirection')} />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(GRADIENT_DIRECTIONS).map(([value, label]) => (
                        <SelectItem key={value} value={value}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="mt-2">
                  <div
                    className="w-full h-20 rounded-lg"
                    style={{
                      background: `linear-gradient(${section.background.direction}, ${section.background.colors?.join(', ')})`
                    }}
                  />
                </div>
              </div>
            )}

            {section.background.type === 'image' && (
              <div className="space-y-4">
                <div>
                  <Label>{t('landing.background.image.label')}</Label>
                  <div className="mt-2 flex items-center space-x-4">
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('imageUpload')?.click()}
                      className="w-full"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      {t('landing.background.image.upload')}
                    </Button>
                    <input
                      id="imageUpload"
                      type="file"
                      accept="image/jpeg,image/png,image/webp,image/gif"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                  </div>
                  {section.background.image && (
                    <div className="mt-4">
                      <img
                        src={section.background.image}
                        alt="Background preview"
                        className="max-h-40 rounded-lg object-cover"
                      />
                    </div>
                  )}
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="buttons" className="space-y-4 mt-4">
            <div className="space-y-3">
              {section.buttons.map((button, index) => (
                <div key={index} className="grid grid-cols-[1fr_1fr_auto] gap-2 p-4 border rounded-lg">
                  <div className="space-y-2">
                    <Label>{t('landing.buttons.textAndColors')}</Label>
                    <Input
                      value={button.text}
                      onChange={(e) => {
                        const newButtons = [...section.buttons]
                        newButtons[index] = { ...button, text: e.target.value }
                        onChange({ ...section, buttons: newButtons })
                      }}
                      placeholder={t('landing.buttons.placeholder')}
                    />
                    <div className="flex items-center space-x-2">
                      <div className="space-y-1">
                        <Label className="text-xs">{t('landing.buttons.textColor')}</Label>
                        <Input
                          type="color"
                          value={button.color}
                          onChange={(e) => {
                            const newButtons = [...section.buttons]
                            newButtons[index] = { ...button, color: e.target.value }
                            onChange({ ...section, buttons: newButtons })
                          }}
                          className="w-full h-8 p-1"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs">{t('landing.buttons.background')}</Label>
                        <Input
                          type="color"
                          value={button.background}
                          onChange={(e) => {
                            const newButtons = [...section.buttons]
                            newButtons[index] = { ...button, background: e.target.value }
                            onChange({ ...section, buttons: newButtons })
                          }}
                          className="w-full h-8 p-1"
                        />
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>{t('landing.buttons.link')}</Label>
                    <div className="flex items-center space-x-2">
                      <Link className="h-4 w-4 text-gray-500" />
                      <Input
                        value={button.link}
                        onChange={(e) => {
                          const newButtons = [...section.buttons]
                          newButtons[index] = { ...button, link: e.target.value }
                          onChange({ ...section, buttons: newButtons })
                        }}
                        placeholder={t('landing.buttons.placeholder')}
                      />
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      const newButtons = section.buttons.filter((_, i) => i !== index)
                      onChange({ ...section, buttons: newButtons })
                    }}
                    className="text-red-500 hover:text-red-600 hover:bg-red-50 self-start mt-8"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              {section.buttons.length < 2 && (
                <Button
                  variant="outline"
                  onClick={() => {
                    const newButton: LandingButton = {
                      text: t('landing.newButton'),
                      link: '#',
                      color: '#ffffff',
                      background: '#000000'
                    }
                    onChange({
                      ...section,
                      buttons: [...section.buttons, newButton]
                    })
                  }}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {t('landing.addButton')}
                </Button>
              )}
            </div>
          </TabsContent>

          <TabsContent value="illustration" className="space-y-4 mt-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>{t('landing.illustration.image')}</Label>
                <Input
                  value={section.illustration?.image.url || ''}
                  onChange={(e) => {
                    if (e.target.value) {
                      onChange({
                        ...section,
                        illustration: {
                          image: { url: e.target.value, alt: section.illustration?.image.alt || '' },
                          position: 'left',
                          verticalAlign: 'center',
                          size: 'medium'
                        }
                      })
                    }
                  }}
                  placeholder={t('landing.illustration.url')}
                />
                <Input
                  value={section.illustration?.image.alt || ''}
                  onChange={(e) => {
                    if (section.illustration?.image.url) {
                      onChange({
                        ...section,
                        illustration: {
                          ...section.illustration,
                          image: { ...section.illustration.image, alt: e.target.value }
                        }
                      })
                    }
                  }}
                  placeholder={t('landing.common.altText')}
                />
                <ImageUploader
                  id="hero-illustration"
                  onImageUploaded={(url) => onChange({
                    ...section,
                    illustration: {
                      image: { url, alt: section.illustration?.image.alt || '' },
                      position: 'left',
                      verticalAlign: 'center',
                      size: 'medium'
                    }
                  })}
                  buttonText={t('landing.illustration.upload')}
                />
                {section.illustration?.image.url && (
                  <img
                    src={section.illustration?.image.url}
                    alt={section.illustration?.image.alt}
                    className="h-12 object-contain"
                  />
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>{t('landing.illustration.position')}</Label>
                  <Select
                    value={section.illustration?.position || 'left'}
                    onValueChange={(value: 'left' | 'right') => onChange({
                      ...section,
                      illustration: {
                        ...section.illustration,
                        position: value,
                        image: section.illustration?.image || { url: '', alt: '' },
                        size: section.illustration?.size || 'medium',
                        verticalAlign: section.illustration?.verticalAlign || 'center'
                      }
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('landing.illustration.selectPosition')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="left">{t('landing.common.left')}</SelectItem>
                      <SelectItem value="right">{t('landing.common.right')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>{t('landing.illustration.size')}</Label>
                  <Select
                    value={section.illustration?.size || 'medium'}
                    onValueChange={(value: 'small' | 'medium' | 'large') => onChange({
                      ...section,
                      illustration: {
                        ...section.illustration,
                        size: value,
                        image: section.illustration?.image || { url: '', alt: '' },
                        position: (section.illustration?.position || 'left') as 'left' | 'right',
                        verticalAlign: section.illustration?.verticalAlign || 'center'
                      }
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('landing.illustration.selectSize')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="small">{t('landing.common.small')}</SelectItem>
                      <SelectItem value="medium">{t('landing.common.medium')}</SelectItem>
                      <SelectItem value="large">{t('landing.common.large')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {section.illustration?.image.url && (
                <Button
                  variant="ghost"
                  onClick={() => onChange({
                    ...section,
                    illustration: undefined
                  })}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50 w-full"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  {t('landing.illustration.remove')}
                </Button>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

interface ImageUploaderProps {
  onImageUploaded: (imageUrl: string) => void
  className?: string
  buttonText?: string
  id: string
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageUploaded, className, buttonText, id }) => {
  const org = useOrg() as any
  const session = useLHSession() as any
  const access_token = session?.data?.tokens?.access_token
  const [isUploading, setIsUploading] = React.useState(false)
  const inputId = `imageUpload-${id}`

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file using reusable utility
    const { validateFile } = await import('@/lib/file-validation')
    const validation = validateFile(file, ['image'])

    if (!validation.valid) {
      toast.error(validation.error!)
      e.target.value = '' // Clear the input
      return
    }

    setIsUploading(true)
    try {
      const response = await uploadLandingContent(org.id, file, access_token)
      if (response.status === 200) {
        const imageUrl = getOrgLandingMediaDirectory(org.org_uuid, response.data.filename)
        onImageUploaded(imageUrl)
        toast.success(t('landing.successImageUpload'))
      } else {
        toast.error(t('landing.errorImageUpload'))
      }
    } catch (error) {
      console.error('Error uploading image:', error)
      toast.error(t('landing.errorImageUpload'))
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className={className}>
      <Button
        variant="outline"
        onClick={() => document.getElementById(inputId)?.click()}
        disabled={isUploading}
        className="w-full"
      >
        <Upload className="h-4 w-4 mr-2" />
        {isUploading ? t('landing.uploading') : (buttonText || t('landing.uploadImageText'))}
      </Button>
      <input
        id={inputId}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={handleFileChange}
        className="hidden"
      />
    </div>
  )
}

const TextAndImageSectionEditor: React.FC<{
  section: LandingTextAndImageSection
  onChange: (section: LandingTextAndImageSection) => void
}> = ({ section, onChange }) => {

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg nice-shadow">
      <div className="flex items-center space-x-2">
        <ImageIcon className="w-5 h-5 text-gray-500" />
        <h3 className="font-medium text-lg">{t('landing.textAndImageSection')}</h3>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <Label htmlFor="title">{t('landing.sectionTitle')}</Label>
          <Input
            id="title"
            value={section.title}
            onChange={(e) => onChange({ ...section, title: e.target.value })}
            placeholder={t('landing.enterSectionTitle')}
          />
        </div>

        {/* Text */}
        <div>
          <Label htmlFor="content">{t('landing.content')}</Label>
          <Textarea
            id="content"
            value={section.text}
            onChange={(e) => onChange({ ...section, text: e.target.value })}
            placeholder={t('landing.enterSectionContent')}
            className="min-h-[100px]"
          />
        </div>

        {/* Flow */}
        <div>
          <Label htmlFor="flow">{t('landing.imagePosition')}</Label>
          <Select
            value={section.flow}
            onValueChange={(value) => onChange({ ...section, flow: value as 'left' | 'right' })}
          >
            <SelectTrigger>
              <SelectValue placeholder={t('landing.selectImagePosition')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="left">{t('landing.common.left')}</SelectItem>
              <SelectItem value="right">{t('landing.common.right')}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Image */}
        <div>
          <Label>{t('landing.background.image.label')}</Label>
          <div className="grid grid-cols-2 gap-4 mt-2">
            <div className="space-y-2">
              <Input
                value={section.image.url}
                onChange={(e) => onChange({
                  ...section,
                  image: { ...section.image, url: e.target.value }
                })}
                placeholder={t('landing.illustration.url')}
              />
              <ImageUploader
                id="text-image-section"
                onImageUploaded={(url) => onChange({
                  ...section,
                  image: { ...section.image, url }
                })}
                buttonText={t('landing.uploadNewImage')}
              />
            </div>
            <div>
              <Input
                value={section.image.alt}
                onChange={(e) => onChange({
                  ...section,
                  image: { ...section.image, alt: e.target.value }
                })}
                placeholder={t('landing.common.altText')}
              />
            </div>
          </div>
          {section.image.url && (
            <div className="mt-4">
              <img
                src={section.image.url}
                alt={section.image.alt}
                className="max-h-40 rounded-lg object-cover"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const LogosSectionEditor: React.FC<{
  section: LandingLogos
  onChange: (section: LandingLogos) => void
}> = ({ section, onChange }) => {

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg nice-shadow">
      <div className="flex items-center space-x-2">
        <Award className="w-5 h-5 text-gray-500" />
        <h3 className="font-medium text-lg">{t('landing.logosSection')}</h3>
      </div>

      <div>
        <Label>{t('landing.logos.label')}</Label>
        <div className="space-y-3 mt-2">
          {/* Title */}
          <div>
            <Label htmlFor="title">{t('landing.sectionTitle')}</Label>
            <Input
              id="title"
              value={section.title}
              onChange={(e) => onChange({ ...section, title: e.target.value })}
              placeholder={t('landing.enterSectionTitle')}
            />
          </div>

          {section.logos.map((logo, index) => (
            <div key={index} className="grid grid-cols-[1fr_1fr_auto] gap-2">
              <div className="space-y-2">
                <Input
                  value={logo.url}
                  onChange={(e) => {
                    const newLogos = [...section.logos]
                    newLogos[index] = { ...logo, url: e.target.value }
                    onChange({ ...section, logos: newLogos })
                  }}
                  placeholder={t('landing.logos.url')}
                />
                <ImageUploader
                  id={`logo-${index}`}
                  onImageUploaded={(url) => {
                    const newLogos = [...section.logos]
                    newLogos[index] = { ...section.logos[index], url }
                    onChange({ ...section, logos: newLogos })
                  }}
                  buttonText={t('landing.logos.upload')}
                />
              </div>
              <div className="space-y-2">
                <Input
                  value={logo.alt}
                  onChange={(e) => {
                    const newLogos = [...section.logos]
                    newLogos[index] = { ...logo, alt: e.target.value }
                    onChange({ ...section, logos: newLogos })
                  }}
                  placeholder={t('landing.common.altText')}
                />
                {logo.url && (
                  <img
                    src={logo.url}
                    alt={logo.alt}
                    className="h-10 object-contain"
                  />
                )}
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  const newLogos = section.logos.filter((_, i) => i !== index)
                  onChange({ ...section, logos: newLogos })
                }}
                className="text-red-500 hover:text-red-600 hover:bg-red-50"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            variant="outline"
            onClick={() => {
              const newLogo: LandingImage = {
                url: '',
                alt: ''
              }
              onChange({
                ...section,
                logos: [...section.logos, newLogo]
              })
            }}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-2" />
            {t('landing.logos.add')}
          </Button>
        </div>
      </div>
    </div>
  )
}

const PeopleSectionEditor: React.FC<{
  section: LandingPeople
  onChange: (section: LandingPeople) => void
}> = ({ section, onChange }) => {

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg nice-shadow">
      <div className="flex items-center space-x-2">
        <Users className="w-5 h-5 text-gray-500" />
        <h3 className="font-medium text-lg">{t('landing.peopleSection')}</h3>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <Label htmlFor="title">{t('landing.sectionTitle')}</Label>
          <Input
            id="title"
            value={section.title}
            onChange={(e) => onChange({ ...section, title: e.target.value })}
            placeholder={t('landing.enterSectionTitle')}
          />
        </div>

        {/* People List */}
        <div>
          <Label>{t('landing.people.label')}</Label>
          <div className="space-y-4 mt-2">
            {section.people.map((person, index) => (
              <div key={index} className="grid grid-cols-[1fr_1fr_1fr_1fr_auto] gap-4 p-4 border rounded-lg">
                <div className="space-y-2">
                  <Label>{t('landing.people.name')}</Label>
                  <Input
                    value={person.name}
                    onChange={(e) => {
                      const newPeople = [...section.people]
                      newPeople[index] = { ...person, name: e.target.value }
                      onChange({ ...section, people: newPeople })
                    }}
                    placeholder={t('landing.people.enterName')}
                  />
                </div>

                <div className="space-y-2">
                  <Label>{t('landing.people.username')}</Label>
                  <Input
                    value={person.username || ''}
                    onChange={(e) => {
                      const newPeople = [...section.people]
                      newPeople[index] = { ...person, username: e.target.value }
                      onChange({ ...section, people: newPeople })
                    }}
                    placeholder="@username"
                  />
                </div>

                <div className="space-y-2">
                  <Label>{t('landing.people.image')}</Label>
                  <div className="space-y-2">
                    <Input
                      value={person.image_url}
                      onChange={(e) => {
                        const newPeople = [...section.people]
                        newPeople[index] = { ...person, image_url: e.target.value }
                        onChange({ ...section, people: newPeople })
                      }}
                      placeholder={t('landing.illustration.url')}
                    />
                    <ImageUploader
                      id={`person-${index}`}
                      onImageUploaded={(url) => {
                        const newPeople = [...section.people]
                        newPeople[index] = { ...section.people[index], image_url: url }
                        onChange({ ...section, people: newPeople })
                      }}
                      buttonText={t('landing.people.upload')}
                    />
                    {person.image_url && (
                      <img
                        src={person.image_url}
                        alt={person.name}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>{t('landing.people.description')}</Label>
                  <Input
                    value={person.description}
                    onChange={(e) => {
                      const newPeople = [...section.people]
                      newPeople[index] = { ...person, description: e.target.value }
                      onChange({ ...section, people: newPeople })
                    }}
                    placeholder={t('landing.people.descriptionPlaceholder')}
                  />
                </div>

                <div className="flex items-end">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      const newPeople = section.people.filter((_, i) => i !== index)
                      onChange({ ...section, people: newPeople })
                    }}
                    className="text-red-500 hover:text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
            <Button
              variant="outline"
              onClick={() => {
                const newPerson = {
                  user_uuid: '',
                  name: '',
                  description: '',
                  image_url: '',
                  username: ''
                }
                onChange({
                  ...section,
                  people: [...section.people, newPerson]
                })
              }}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              {t('landing.people.add')}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

const FeaturedCoursesEditor: React.FC<{
  section: LandingFeaturedCourses
  onChange: (section: LandingFeaturedCourses) => void
}> = ({ section, onChange }) => {
  const org = useOrg() as any
  const session = useLHSession() as any
  const access_token = session?.data?.tokens?.access_token

  const { data: courses } = useSWR(
    org?.slug ? [org.slug, access_token] : null,
    ([orgSlug, token]) => getOrgCourses(orgSlug, null, token)
  )

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg nice-shadow">
      <div className="flex items-center space-x-2">
        <BookOpen className="w-5 h-5 text-gray-500" />
        <h3 className="font-medium text-lg">{t('landing.coursesSection')}</h3>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <Label htmlFor="title">{t('landing.sectionTitle')}</Label>
          <Input
            id="title"
            value={section.title}
            onChange={(e) => onChange({ ...section, title: e.target.value })}
            placeholder={t('landing.enterSectionTitle')}
          />
        </div>

        {/* Course Selection */}
        <div>
          <Label>{t('landing.courses.select')}</Label>
          <div className="space-y-4 mt-2">
            {courses ? (
              <div className="grid gap-4">
                {courses.map((course: any) => (
                  <div
                    key={course.course_uuid}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-100 rounded-md overflow-hidden">
                        {course.course_thumbnail && (

                          <img
                            src={course.course_thumbnail}
                            alt={course.name}
                            className="w-full h-full object-cover"
                          />
                        )}
                      </div>
                      <div>
                        <h4 className="font-medium">{course.name}</h4>
                        <p className="text-sm text-gray-500">{course.description}</p>
                      </div>
                    </div>
                    <Button
                      variant={section.courses.includes(course.course_uuid) ? "default" : "outline"}
                      onClick={() => {
                        const newCourses = section.courses.includes(course.course_uuid)
                          ? section.courses.filter(id => id !== course.course_uuid)
                          : [...section.courses, course.course_uuid]
                        onChange({ ...section, courses: newCourses })
                      }}
                      className={section.courses.includes(course.course_uuid) ? "bg-black hover:bg-black/90" : ""}
                    >
                      {section.courses.includes(course.course_uuid) ? t('landing.courses.selected') : t('landing.courses.selectButton')}
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                {t('landing.courses.loading')}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default OrgEditLanding 