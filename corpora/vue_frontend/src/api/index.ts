import axios from 'axios'

export const getRandomRecording = () => {
  return axios.get(`/api/listen/?random=True`, config )
}
