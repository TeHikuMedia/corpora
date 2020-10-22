export const getCookie = (key: string) => {
  const regexp = new RegExp(`.*${key}=([^;]*)`)
  const result = regexp.exec(document.cookie)
  if (result) {
    return result[1]
  } else {
    throw new Error('Unable to parse cookie')
  }
}
