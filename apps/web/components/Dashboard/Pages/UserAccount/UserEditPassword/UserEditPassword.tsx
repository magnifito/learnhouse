import { useLHSession } from '@components/Contexts/LHSessionContext'
import { updatePassword } from '@services/settings/password'
import { Formik, Form } from 'formik'
import React, { useEffect } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Input } from "@components/ui/input"
import { Button } from "@components/ui/button"
import { Label } from "@components/ui/label"
import { toast } from 'react-hot-toast'
import { signOut } from 'next-auth/react'
import { getUriWithoutOrg } from '@services/config/config'
import * as Yup from 'yup'
import { useTranslations } from 'next-intl'

const createValidationSchema = (t: any) => Yup.object().shape({
  old_password: Yup.string().required(t('currentPasswordRequired')),
  new_password: Yup.string()
    .required(t('newPasswordRequired'))
    .min(8, t('passwordMinLength')),
})

function UserEditPassword() {
  const t = useTranslations('settings')
  const session = useLHSession() as any
  const access_token = session?.data?.tokens?.access_token;
  const validationSchema = createValidationSchema(t)

  const updatePasswordUI = async (values: any) => {
    const loadingToast = toast.loading(t('updatingPassword'))
    try {
      let user_id = session.data.user.id
      const response = await updatePassword(user_id, values, access_token)

      if (response.success) {
        toast.dismiss(loadingToast)

        // Show success message and notify about logout
        toast.success(t('passwordUpdatedSuccess'), { duration: 4000 })
        toast((toastInstance: any) => (
          <div className="flex items-center gap-2">
            <span>{t('pleaseLoginWithNewPassword')}</span>
          </div>
        ), {
          duration: 4000,
          icon: '🔑'
        })

        // Wait for 4 seconds before signing out
        await new Promise(resolve => setTimeout(resolve, 4000))
        signOut({ redirect: true, callbackUrl: getUriWithoutOrg('/') })
      } else {
        toast.error(response.data.detail || t('failedToUpdatePassword'), { id: loadingToast })
      }
    } catch (error: any) {
      const errorMessage = error.data?.detail || t('failedToUpdatePasswordTryAgain')
      toast.error(errorMessage, { id: loadingToast })
      console.error('Password update error:', error)
    }
  }

  useEffect(() => { }, [session])

  return (
    <div className="sm:mx-10 mx-0 bg-white rounded-xl nice-shadow">
      <div className="flex flex-col">
        <div className="flex flex-col bg-gray-50 -space-y-1 px-5 py-3 mx-3 my-3 rounded-md">
          <h1 className="font-bold text-xl text-gray-800">
            {t('changePassword')}
          </h1>
          <h2 className="text-gray-500 text-md">
            {t('changePasswordDescription')}
          </h2>
        </div>

        <div className="px-8 py-6">
          <Formik
            initialValues={{ old_password: '', new_password: '' }}
            validationSchema={validationSchema}
            onSubmit={(values, { setSubmitting }) => {
              setTimeout(() => {
                setSubmitting(false)
                updatePasswordUI(values)
              }, 400)
            }}
          >
            {({ isSubmitting, handleChange, errors, touched }) => (
              <Form className="w-full max-w-2xl mx-auto space-y-6">
                <div>
                  <Label htmlFor="old_password">{t('currentPassword')}</Label>
                  <Input
                    type="password"
                    id="old_password"
                    name="old_password"
                    onChange={handleChange}
                    className="mt-1"
                  />
                  {touched.old_password && errors.old_password && (
                    <p className="text-red-500 text-sm mt-1">{errors.old_password}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="new_password">{t('newPassword')}</Label>
                  <Input
                    type="password"
                    id="new_password"
                    name="new_password"
                    onChange={handleChange}
                    className="mt-1"
                  />
                  {touched.new_password && errors.new_password && (
                    <p className="text-red-500 text-sm mt-1">{errors.new_password}</p>
                  )}
                </div>

                <div className="flex items-center space-x-2 text-amber-600 bg-amber-50 p-3 rounded-md">
                  <AlertTriangle size={16} />
                  <span className="text-sm">{t('loggedOutAfterPasswordChange')}</span>
                </div>

                <div className="flex justify-end pt-2">
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="bg-black text-white hover:bg-black/90"
                  >
                    {isSubmitting ? t('updating') : t('updatePassword')}
                  </Button>
                </div>
              </Form>
            )}
          </Formik>
        </div>
      </div>
    </div>
  )
}

export default UserEditPassword
