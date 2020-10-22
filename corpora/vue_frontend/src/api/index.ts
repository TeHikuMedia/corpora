import axios from 'axios'
import { headerBuilder } from './helpers'

export const getRandomRecording = () => {
  return axios.get('/api/recordings/?sort_by=random')
}

export const postRecordingQC = (payload: any) => {
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
