import axios from 'axios'

export const getRandomRecording = () => {
  return axios.get('/api/recordings/?sort_by=random')
}
