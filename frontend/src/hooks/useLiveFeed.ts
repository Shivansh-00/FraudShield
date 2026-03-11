import { useEffect } from 'react'
import { getWsUrl } from '../services/api'

export const useLiveFeed = (onMessage: (payload: any) => void) => {
  useEffect(() => {
    const ws = new WebSocket(getWsUrl())
    ws.onopen = () => ws.send('subscribe')
    ws.onmessage = (event) => onMessage(JSON.parse(event.data))
    return () => ws.close()
  }, [onMessage])
}
