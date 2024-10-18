<script setup lang="ts">
import {onMounted, ref} from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import {authService} from '@/services/authService'
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";

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
</script>

<template>
  <div class="type1">
    <header>
      <logo-intro-screen/>
    </header>
    <div class="container">
      <start-blend-button />
    </div>
    <div id="app" class="login-container">
      <Button @click="redirectToSpotify" class="spotify-button">
        Login via Spotify
      </Button>

      <div class="guest-login">
        <label for="guestInput">Login as guest</label>
        <div class="input-group">
          <InputText id="guestInput" type="text" placeholder="Username" v-model="username" @keyup.enter="authorize"/>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: grid;
  grid-auto-rows: 40px;
  grid-template-areas:
    "spotify"
    "guest";
  gap: 20px;
  justify-items: center;
  margin-top: 50px;
}

.spotify-button {
  grid-area: spotify;
  background-color: #1db954;
  color: white;
  padding: 8px 16px; /* Reduced padding */
  border: none;
  border-radius: 25px;
  font-size: 14px; /* Reduced font size */
  cursor: pointer;
  height: 40px;
}

.guest-login {
  grid-area: guest;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input-group {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.input-group input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.input-group i {
  margin-left: -30px;
  cursor: pointer;
}
</style>