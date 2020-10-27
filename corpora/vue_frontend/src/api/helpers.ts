import { getCookie } from '@/helpers/cookie'

interface Header {
  'Content-Type'?: ContentType;
  'X-CSRFToken'?: string;
}

type ContentType = 'application/json' | 'multipart/form-data'

export const headerBuilder = (config: {contentType?: ContentType; includeCSRFToken?: boolean}) => {
  const header: Header = {}

  if (config.contentType) {
    header['Content-Type'] = config.contentType
  }

  if (config.includeCSRFToken) {
    header['X-CSRFToken'] = getCookie('csrftoken')
  }

  return header
}
