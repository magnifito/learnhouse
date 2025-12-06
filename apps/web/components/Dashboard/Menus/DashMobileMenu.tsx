'use client'
import { useOrg } from '@components/Contexts/OrgContext'
import { Backpack, BadgeDollarSign, BookCopy, Home, School, Settings, Users } from 'lucide-react'
import Link from 'next/link'
import React from 'react'
import AdminAuthorization from '@components/Security/AdminAuthorization'
import { useLHSession } from '@components/Contexts/LHSessionContext'
import ToolTip from '@components/Objects/StyledElements/Tooltip/Tooltip'
import { useTranslations } from 'next-intl'

function DashMobileMenu() {
  const t = useTranslations()
  const org = useOrg() as any
  const session = useLHSession() as any

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-black/90 backdrop-blur-lg text-white shadow-xl">
      <div className="flex justify-around items-center h-16 px-2">
        <AdminAuthorization authorizationMode="component">
          <ToolTip content={t('navigation.home')} slateBlack sideOffset={8} side="top">
            <Link href={`/`} className="flex flex-col items-center p-2" aria-label="Go to dashboard home">
              <Home size={20} />
              <span className="text-xs mt-1">{t('navigation.home')}</span>
            </Link>
          </ToolTip>
          <ToolTip content={t('navigation.courses')} slateBlack sideOffset={8} side="top">
            <Link href={`/dash/courses`} className="flex flex-col items-center p-2" aria-label="Manage courses">
              <BookCopy size={20} />
              <span className="text-xs mt-1">{t('navigation.courses')}</span>
            </Link>
          </ToolTip>
          <ToolTip content={t('navigation.assignments')} slateBlack sideOffset={8} side="top">
            <Link href={`/dash/assignments`} className="flex flex-col items-center p-2" aria-label="Manage assignments">
              <Backpack size={20} />
              <span className="text-xs mt-1">{t('navigation.assignments')}</span>
            </Link>
          </ToolTip>
          <ToolTip content={t('navigation.payments')} slateBlack sideOffset={8} side="top">
            <Link href={`/dash/payments/customers`} className="flex flex-col items-center p-2" aria-label="Manage payments and billing">
              <BadgeDollarSign size={20} />
              <span className="text-xs mt-1">{t('navigation.payments')}</span>
            </Link>
          </ToolTip>
          <ToolTip content={t('navigation.users')} slateBlack sideOffset={8} side="top">
            <Link href={`/dash/users/settings/users`} className="flex flex-col items-center p-2" aria-label="Manage users">
              <Users size={20} />
              <span className="text-xs mt-1">{t('navigation.users')}</span>
            </Link>
          </ToolTip>
          <ToolTip content={t('navigation.organization')} slateBlack sideOffset={8} side="top">
            <Link href={`/dash/org/settings/general`} className="flex flex-col items-center p-2" aria-label="Organization settings">
              <School size={20} />
              <span className="text-xs mt-1">{t('navigation.organization')}</span>
            </Link>
          </ToolTip>
        </AdminAuthorization>
        <ToolTip content={t('userSettings', { username: session.data.user.username })} slateBlack sideOffset={8} side="top">
          <Link href={'/dash/user-account/settings/general'} className="flex flex-col items-center p-2" aria-label="User account settings">
            <Settings size={20} />
            <span className="text-xs mt-1">{t('navigation.settings')}</span>
          </Link>
        </ToolTip>
      </div>
    </div>
  )
}

export default DashMobileMenu
