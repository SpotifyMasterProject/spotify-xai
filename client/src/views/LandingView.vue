<script setup lang="ts">
import {onMounted, ref} from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import {authService} from '@/services/authService'
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";
import StartBlendButton from "@/components/StartBlendButton.vue";
import Navigation from "@/components/Navigation.vue";
import StartScreen from '@/components/StartScreen.vue';


const showStartScreen = ref(true);
const username = ref<string>('')

const urlParams = new URLSearchParams(window.location.search)
const code = urlParams.get('code')
const state = urlParams.get('state')

onMounted(async () => {
  if (code != null) {
    await authService.authorizeSpotify('username_placeholder', code)
        .then((response) => {
          console.log(response)
        })
        .catch((error) => {
          console.log(error)
        })
  }
})

const redirectToSpotify = async () => {
  window.location.href = 'https://accounts.spotify.com/authorize?' +
      'response_type=' + 'code' +
      '&client_id=' + import.meta.env.VITE_SPOTIFY_CLIENT_ID +
      //'&scope' +
      '&redirect_uri=' + import.meta.env.VITE_SPOTIFY_REDIRECT_URI
      //'&state='
}

const authorize = function () {
  if (username.value === '') {
    return
  }
  authService.authorize(username.value)
      .catch((error) => {
        console.log(error)
      })
}

const handleComplete = () => {
  showStartScreen.value = false;
}
</script>

<template>
  <div>
    <transition name="fade">
      <StartScreen v-if="showStartScreen" @animation-complete="handleComplete" key="start-screen" />
      <div class="type1" v-else>
        <header>
          <LogoIntroScreen/>
          <nav>
            <Navigation />
          </nav>
        </header>
        <div class="container">
          <StartBlendButton />
        </div>
      </div>
    </transition>
  </div>
</template>


<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter, .fade-leave-to /* .fade-leave-active in Vue 2 */ {
  opacity: 0;
}
</style>