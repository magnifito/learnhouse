import { useOrg } from '@components/Contexts/OrgContext'
import React from 'react'

interface UseGetAIFeatures {
  feature: 'editor' | 'activity_ask' | 'course_ask' | 'global_ai_ask'
}

function useGetAIFeatures(props: UseGetAIFeatures) {
  const org = useOrg() as any
  const [isEnabled, setisEnabled] = React.useState(false)

  function checkEnvAIEnabled(): boolean {
    // Check environment variable for global AI disable flag
    if (typeof window !== 'undefined') {
      const runtimeConfig = (window as any).__RUNTIME_CONFIG__
      const envValue = runtimeConfig?.NEXT_PUBLIC_LEARNHOUSE_AI_ENABLED || 
                      process.env.NEXT_PUBLIC_LEARNHOUSE_AI_ENABLED
      
      // If explicitly set, respect it
      if (envValue !== undefined) {
        return envValue === 'true' || envValue === '1' || envValue === 'yes'
      }
    }
    
    // Check server-side env var (for SSR)
    if (typeof window === 'undefined') {
      const envValue = process.env.NEXT_PUBLIC_LEARNHOUSE_AI_ENABLED || 
                      process.env.LEARNHOUSE_IS_AI_ENABLED
      if (envValue !== undefined) {
        return envValue === 'true' || envValue === '1' || envValue === 'yes'
      }
    }
    
    // Default to true if not set (backward compatibility)
    return true
  }

  function checkAvailableAIFeaturesOnOrg(feature: string): boolean {
    // First check env-level setting - if disabled at env level, AI is disabled globally
    const envEnabled = checkEnvAIEnabled()
    if (!envEnabled) {
      return false
    }

    // Then check organization-level setting
    const orgConfig = org?.config?.config?.features?.ai?.enabled
    
    // If org config explicitly says false, disable
    if (orgConfig === false) {
      return false
    }
    
    // If org config is true or undefined, and env allows it, enable
    return orgConfig === true || orgConfig === undefined
  }

  React.useEffect(() => {
    if (org || typeof org === 'undefined') {
      // Check if org is not null or undefined (org can be undefined initially)
      let isEnabledStatus = checkAvailableAIFeaturesOnOrg(props.feature)
      setisEnabled(isEnabledStatus)
    } else {
      // If org is explicitly null, check only env level
      setisEnabled(checkEnvAIEnabled())
    }
  }, [org, props.feature])

  return isEnabled
}

export default useGetAIFeatures
