import { ref, onUnmounted } from 'vue'

export interface SSEEvent {
  event: string
  data: any
}

export function useSSE() {
  const isConnected = ref(false)
  const error = ref<string | null>(null)
  let eventSource: EventSource | null = null

  function connect(
    url: string,
    handlers: Record<string, (data: any) => void>,
    options?: { onOpen?: () => void; onError?: (err: Event) => void }
  ) {
    if (eventSource) {
      disconnect()
    }

    eventSource = new EventSource(url)

    eventSource.onopen = () => {
      isConnected.value = true
      error.value = null
      options?.onOpen?.()
    }

    eventSource.onerror = (e) => {
      error.value = 'Connection error'
      isConnected.value = false
      options?.onError?.(e)
    }

    // Register event handlers
    Object.entries(handlers).forEach(([eventType, handler]) => {
      eventSource!.addEventListener(eventType, (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data)
          handler(data)
        } catch (e) {
          console.error('Failed to parse SSE data:', e)
        }
      })
    })

    // Handle generic messages
    eventSource.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        handlers['message']?.(data)
      } catch (e) {
        console.error('Failed to parse SSE message:', e)
      }
    }
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close()
      eventSource = null
      isConnected.value = false
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    error,
    connect,
    disconnect,
  }
}
