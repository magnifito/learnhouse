'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'

type NewCourseButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement>

const NewCourseButton = React.forwardRef<HTMLButtonElement, NewCourseButtonProps>(
  ({ className = '', ...props }, ref) => {
    const t = useTranslations('courses')

    return (
      <button
        ref={ref}
        type="button"
        className={
          'rounded-lg bg-black hover:scale-105 transition-all duration-100 ease-linear antialiased ring-offset-purple-800 p-2 px-5 my-auto text-xs font-bold text-white drop-shadow-lg flex space-x-2 items-center ' +
          className
        }
        {...props}
      >
        <div>{t('createCourse')}</div>
        <div className="text-md bg-neutral-800 px-1 rounded-full">+</div>
      </button>
    )
  }
)

NewCourseButton.displayName = 'NewCourseButton'

export default NewCourseButton
