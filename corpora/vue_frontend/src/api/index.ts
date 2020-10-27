import axios from 'axios'
import { headerBuilder } from './helpers'
import { PostRecordingQualityControl } from '@/api/interfaces'

export const getRandomRecording = () => {
  return axios.get('/api/recordings/?sort_by=random')
}

export const postRecordingQC = (payload: PostRecordingQualityControl) => {
  const config = { headers: headerBuilder({ contentType: 'application/json', includeCSRFToken: true }) }
  return axios.post('/api/recordingqualitycontrol/', payload, config)
}

export const getMyself = () => {
  return axios.get('/api/profile/')
    .then((response) => {
      return response.data.results[0].id
    })
    .catch(() => {
      return null
    })
}

export const updateRecordingText = (id: number, sentence_text: string) => {
  const config = { headers: headerBuilder({ contentType: 'application/json', includeCSRFToken: true }) }
  const url = `/api/recording/${id}`
  return axios.put(
    url,
    {
      id: id,
      sentence_text: sentence_text
    },
    config
  )
}
