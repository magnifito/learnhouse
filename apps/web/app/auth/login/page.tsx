import { getOrganizationContextInfo } from '@services/organizations/orgs'
import LoginClient from './login'
import { Metadata } from 'next'

type MetadataProps = {
  params: Promise<{ orgslug: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}

export async function generateMetadata(params: MetadataProps): Promise<Metadata> {
  const orgslug = (await params.searchParams).orgslug

  //const orgslug = params.orgslug
  // Get Org context information
  const org = await getOrganizationContextInfo(orgslug, {
    revalidate: 0,
    tags: ['organizations'],
  })

  return {
    title: 'Login' + ` — ${org.name}`,
  }
}

import { getServerSession } from 'next-auth'
import { nextAuthOptions } from '../options'
import { redirect } from 'next/navigation'

const Login = async (params: MetadataProps) => {
  const session = await getServerSession(nextAuthOptions)
  if (session) {
    redirect('/')
  }

  const orgslug = (await params.searchParams).orgslug
  const org = await getOrganizationContextInfo(orgslug, {
    revalidate: 0,
    tags: ['organizations'],
  })

  return (
    <div>
      <LoginClient org={org}></LoginClient>
    </div>
  )
}

export default Login
