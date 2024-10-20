<script setup lang="ts">
import {onBeforeUnmount, onMounted, ref} from 'vue'
import WebsocketService from '@/services/websocketService'
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";

const receivedMessages = ref<string[]>([])
const wsService = new WebsocketService()

const handleMessage = (message: any) => {
  receivedMessages.value.push(message)
}

onMounted(() => {
  wsService.setMessageHandler(handleMessage)
})

onBeforeUnmount(() => {
  wsService.close()
})
</script>

<template>
  <div class="type1">
    <header>
      <logo-intro-screen/>
    </header>
    <div class = type2>
      <h1>WebSocket Example</h1>
      <h2>Received Messages:</h2>
      <div v-if="receivedMessages.length">
        <div v-for="(msg, index) in receivedMessages" :key="index">
          <pre>{{ msg }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>