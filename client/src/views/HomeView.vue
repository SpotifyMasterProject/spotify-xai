<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref, onMounted, computed } from "vue";
import { Session } from "@/types/Session";
import { useAuthStore } from "@/stores/auth";
import { useSession } from "@/stores/session";
import { useRouter, useRoute } from 'vue-router';
import Navigation from "@/components/Navigation.vue";
import MainVisualization from "@/components/MainVisualization.vue";
import VisualizationAid from '@/components/VisualizationAid.vue';
import Button from 'primevue/button';
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";
import QrcodeVue from 'qrcode.vue'
import AddMoreSong from "@/components/AddMoreSong.vue";
import Sidebar from "primevue/sidebar";
import StartBlendButton from "@/components/StartBlendButton.vue";
import PlaylistCreator from "@/components/PlaylistCreator.vue";
import MobileMainViz from "@/components/MobileMainViz.vue";
import { Playlist, flattenPlaylist } from "@/types/Playlist";
import {getSongFeatures, sessionService} from "@/services/sessionService";
import SongFeatureDialog from "@/components/SongFeatureDialog.vue";
import {SongFeatureCategory} from "@/types/SongFeature";

const showSongFeatureDialog = ref(false);
const showAddMoreSongPopup = ref(false);

const showVisualizationAid = ref(false);

const LOCAL_IP_ADDRESS = import.meta.env.VITE_LOCAL_IP_ADDRESS;

const toggleVisibility = () => {
  showSongFeatureDialog.value = !showSongFeatureDialog.value;
  selectedFeature.value = null;
};


const router = useRouter();
const route = useRoute();

const settingsVisible = ref(false);
const sessionEnded = ref(false);

const authStore = useAuthStore();
const isHost = authStore.user?.isHost ?? false;
const errorMessage = ref();
const loading = ref(true);
const sessionStore = useSession();
const {session} = storeToRefs(sessionStore);

onMounted(async () => {
  await router.isReady();

  const sessionId = isHost ? null : route.params.sessionId;

  try {
    await sessionStore.fetchSession(sessionId);
  } catch (error) {
    if (!isHost) {
      errorMessage.value = "Could not find session. Please try to join again."
    }
  }
  
  loading.value = false;
});

const toggleAddMoreSongPopup = () => {
  showAddMoreSongPopup.value = !showAddMoreSongPopup.value;
};

const createNewSessionFlow = ref(false);
const runningSession = ref();

const startSession = async (newSession) => {
  await sessionStore.createSession(newSession);
  createNewSessionFlow.value = false;
  selectedSessionIndex.value = 0;

  showVisualizationAid.value = true;
};

//Information Button to read more about how the visualization can be read
const infoVisible = ref(true);
function toggleInfo(){
  console.log("toggle");
  showVisualizationAid.value = !showVisualizationAid.value;
}
const closeVisualizationAid = () => {
  showVisualizationAid.value = false;
};

const showSettings = () => {
  settingsVisible.value = true;
};

const removeGuest = async (guestId) => {
  await sessionService.removeGuest(session.value.id, guestId);
};

const endCurrentSession = async () => {
  await sessionStore.endSession();
  settingsVisible.value = false;
};

const flowerData = computed(() => {
  if (session.value && session.value.playlist) {
    return flattenPlaylist(session.value.playlist).map(getSongFeatures);
  }
  return [];
});

const selectedFeature = ref(null);
function handleFlowerSelected(index, featureCategory) {
  console.log("flower index received", index, featureCategory)
  selectedFeature.value = {index, featureCategory};
  showSongFeatureDialog.value = true;
}
</script>

<template>
  <div class="type2">
    <header>
      <div class="function-icon-container" v-if="session?.isRunning">
        <Button icon="pi pi-search" severity="success" text raised rounded aria-label="Search" @click="toggleAddMoreSongPopup" />
      </div>
      <div class="logo-nav-container">
        <logo-intro-screen/>
      </div>
      <i v-if="isHost && session?.isRunning" class="settings-icon pi pi-cog" @click="showSettings()"></i>
    </header>
    <div class="middle" v-if="!loading">
      <div v-if="errorMessage" class="error">
          {{errorMessage}}
      </div>
      <div v-else-if="!session && isHost">
        <start-blend-button v-if="!createNewSessionFlow" @click="createNewSessionFlow = true" />
        <playlist-creator v-else @startSession="startSession"></playlist-creator>
      </div>
      <template v-else>
        <div class="info-box" :class="{ active: showVisualizationAid }" @click="toggleInfo">
          <div> i </div>
        </div>
        <MainVisualization v-if="isHost" :session="session" @flowerSelected="handleFlowerSelected"/>
        <MobileMainViz v-if="!isHost" :session="session" />
      </template>
    </div>
    <div v-if="session && session.isRunning" class="footer-section">
      <div
        class="song-feature-dialog"
        :class="{ minimized: !showSongFeatureDialog }"
      >
        <div class="table-header-container">
          <h3>Audio Feature Chart</h3>
          <button
            class="text-sm rounded min-h-[32px] px-3 py-0.5 font-semibold hover:bg-gray-800"
            @click="toggleVisibility"
          >
            <i :class="showSongFeatureDialog ? 'pi pi-chevron-down' : 'pi pi-chevron-left' "></i>
          </button>
        </div>
        <div v-show="showSongFeatureDialog" class="song-feature">
          <SongFeatureDialog
              :flowerData="flowerData"
              :selectedFeature="selectedFeature"
          />
        </div>
      </div>
      <qrcode-vue v-if="isHost" :value="session.inviteLink" />
    </div>
    <!-- Conditionally render VisualizationAid component -->
    <VisualizationAid v-if="showVisualizationAid" @close-popup="closeVisualizationAid" />
    <!-- Popup Overlay -->
    <div v-if="showAddMoreSongPopup" class="popup-overlay" @click="toggleAddMoreSongPopup">
      <div class="popup-content" @click.stop>
        <AddMoreSong
          @close-popup="toggleAddMoreSongPopup"
          :sessionId="session.id" />
      </div>
    </div>
    <Sidebar v-model:visible="settingsVisible" header="Settings" :unstyled="false">
       <h3>Guests</h3>
       <div class="guests-container">
        <div v-for="guest in session.guests" class="guest" :key="session.guests.length">
          {{guest.username}}
          <i class="delete-guest-icon pi pi-trash" @click="removeGuest(guest.id)"/>
        </div>
      </div>

       <button class="end-session-button" @click="endCurrentSession()">
        End Session
       </button>
    </Sidebar>
  </div>
</template>

<style scoped>
.function-icon-container {
  position: absolute;
  top: 10px;
  left: 30px;
  z-index: 1000;
}

.function-icon-container button {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #6BA149;
  color: #D9D9D9;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  border-radius: 25%;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.function-icon-container button:hover {
  background-color: #6AA834;
  transform: scale(1.05);
}

.song-feature-dialog.minimized{
  height: auto;
}

.song-feature-dialog{
  background-color: var(--backcore-color1);
  padding: 0 0 15px 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: flex-start;
  justify-content: flex-start;
  overflow-y: hidden;
  box-sizing: border-box;
  border-radius: 18px;
  text-align: left;
  color: #FFFFFF;
  transition: all 0.5s ease;
  max-height: 40vh;
  width: 100%;
}

.song-feature-dialog .table-header-container {
  display: flex;
  flex-direction: row;  /* Aligns the header and button horizontally */
  align-items: center;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: #272525;
  padding-bottom: 0;
  margin-bottom: 0;
}
.song-feature-dialog.minimized .table-header-container {
  padding-bottom: 0; /* No padding when minimized */
}

.song-feature-dialog h3 {
  margin: 10px 0 0 10px;
  font-size: 18px;
  width: 100%;
}
.song-feature-dialog button {
  position: sticky;
  right: 0;
  z-index: 1001;
  padding: 4px 8px;
  background-color: #6BA149;
  color: #D9D9D9;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.2s ease;
}
.song-feature-dialog button:hover {
  background-color: #6AA834;
  transform: scale(1.05); /* Slightly enlarge the button on hover */
}
.song-feature-dialog .table-scroll {
  overflow-y: auto;
  overflow-x: auto;
}

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 1000;
}

.footer-section {
  display: flex;
  flex-direction: row;
  margin: 0 20px 20px;
  gap: 8px;
  justify-content: space-between;
}

.song-feature {
  display: flex;
  width: 100%;
  height: 100%;
  padding: 10px;
  overflow-y: scroll;
  background-color: var(--backcore-color3);
  box-sizing: border-box;
}

.settings-icon {
    position: absolute;
    right: 30px;
    color: var(--logo-highlight-color);
    font-size: 30px;
    cursor: pointer;
}

.visualization {
  display: contents;
}

.error {
  color: var(--font-color);
}

/* Adjust for better placement on mobile */
@media (max-width: 600px) {
  .function-icon-container {
    top: 30px;
    left: 30px;
  }

  .function-icon-container button {
    width: 35px;
    height: 35px;
    font-size: 14px;
  }

  .song-feature-dialog {
    padding: 10px;
    max-height: 300px;
  }

  .song-feature-dialog .table-header-container {
    padding-bottom: 0;
    margin-bottom: 0;
  }

  .song-feature-dialog h3 {
    font-size: 14px;
  }

  .song-feature-dialog button {
    font-size: 12px;
    padding: 4px 8px;
  }

  .song-feature-dialog .table-scroll {
    max-height: 300px;
    margin-top: 0;
    padding-top: 0;
  }
}
.guest {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.delete-guest-icon {
  cursor: pointer;
}
.end-session-button {
  position: absolute;
  font-size: 16px;
  background-color: var(--logo-highlight-color);
  border-radius: 12px;
  border: none;
  padding: 8px 20px;
  cursor: pointer;
  font-weight: bold;
  color: white;
}
.guests-container {
  height: 60%;
  overflow: scroll;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
