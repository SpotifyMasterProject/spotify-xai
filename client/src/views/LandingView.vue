<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/stores/auth';
import { sessionService } from '@/services/sessionService';
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";
import StartBlendButton from "@/components/StartBlendButton.vue";
import StartScreen from '@/components/StartScreen.vue';
import { isMobile } from "@/services/layoutService";

const showStartScreen = ref(true);
const username = ref<string>('');
const invitedSession = ref();
const hostUsername = computed(() => {
  return invitedSession.value ? invitedSession.value.hostName : "";
});

const router = useRouter();
const route = useRoute();

onMounted(async () => {
  await router.isReady();
  const sessionId = route.params.sessionId;
  if (sessionId) {
    invitedSession.value = await sessionService.getSessionById(sessionId);
  }
});

const redirectToSpotify = async () => {
  window.location.href = 'https://accounts.spotify.com/authorize?' +
      'response_type=' + 'code' +
      '&client_id=' + import.meta.env.VITE_SPOTIFY_CLIENT_ID +
      //'&scope' +
      '&redirect_uri=' + import.meta.env.VITE_SPOTIFY_REDIRECT_URI
      //'&state='
}

const handleComplete = () => {
  showStartScreen.value = false;
}

const joinSession = async (sessionId) => {
  if (!username.value) {
    return;
  }

  const authStore = useAuthStore();

  try {
    await authService.authorize(username.value);
    const guestSession = await sessionService.joinSession(sessionId);
    router.push({path: `/session/${guestSession.id}`});
  } catch (error) {
    console.log(error);
    await authStore.deauthorize();
  }
}

</script>

<template>
  <div>
    <transition name="fade">
      <StartScreen v-if="showStartScreen" @animation-complete="handleComplete" key="start-screen" />
      <div class="type1" v-else>
        <header>
          <LogoIntroScreen/>
        </header>
        <div class="login-container">
          <Button v-if="
            !$route.params.sessionId && !isMobile" class="button spotify-button" @click="redirectToSpotify">
            Login via Spotify
          </Button>
          <div v-else-if="!$route.params.sessionId">
            Please use computer to login as host
          </div>
          <div v-else class="guest-login">
            <p class="invite-text">
              You have been invited to
              <span class="highlight">a new blend!</span>
            </p>
            <p class="host-info">
              <strong>{{ hostUsername }}</strong>
              invited you to the blend. Enter username to join.</p>
            <InputText id="username" v-model="username" placeholder="Username" class="input-default" />
            <Button
              @click="() => joinSession($route.params.sessionId)"
              class="join-button"
              :disabled="!username.length">Join</Button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>


<style scoped>

.login-container {
  --login-container-height: 200px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  justify-items: center;
  align-items: center;
  width: 200px;
  position: absolute;
  height: var(--login-container-height);
  top: calc(50% - var(--login-container-height) / 2);
}

.guest-login {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  background-color: var(--backcore-color3);
  border-radius: 10px;
  width: 200px;
  padding:20px;
}


.invite-text {
  color: white;
  font-size: 16px;
  font-weight: bold;
  font-style: italic;
  text-align: center;
}

.highlight {
  color: var(--logo-highlight-color);
}

.guest-login input {
  color: white;
}

.join-button {
  background-color: var(--logo-highlight-color);
  color: white;
  width: 80%;
  border: none;
  border-radius: 25px;
  font-size: 14px;
  height: 30px;
  font-weight: bold;
}

.join-button:disabled {
  color: var(--button-disabled-font-color);
}

.host-info {
  color: white;
  font-size: 14px;
  text-align: center;
}

.button {
  padding: 8px 16px; /* Reduced padding */
  border: none;
  border-radius: 25px;
  font-size: 14px; /* Reduced font size */
  cursor: pointer;
  height: 40px;
}

.spotify-button {
  background-color: #1db954;
  color: white;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter, .fade-leave-to /* .fade-leave-active in Vue 2 */ {
  opacity: 0;
}

</style>