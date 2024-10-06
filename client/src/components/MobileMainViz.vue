<script setup lang="ts">
import Flower from "@/components/Flower.vue";
import {SongFeatureCategory} from '@/types/SongFeature';
import {ref, onMounted, onUnmounted} from 'vue';
import {useAuthStore} from "@/stores/auth";
import {sessionService} from "@/services/sessionService";
import {SessionWebsocketService} from "@/services/sessionWebsocketService";
import { SessionMessageType } from "@/types/SessionMessage";

const sessionSocket = new SessionWebsocketService();

const props = defineProps<{
  sessionId: string,
}>();

const songList = ref([
  { title: "Baby Powder", artist: "Jenevieve", features: [
      { category: SongFeatureCategory.ENERGY, value: 0.4 },
      { category: SongFeatureCategory.DANCEABILITY, value: 0.6 },
      { category: SongFeatureCategory.SPEECHINESS, value: 0.5 },
      { category: SongFeatureCategory.VALENCE, value: 0.3 },
      { category: SongFeatureCategory.TEMPO, value: 0.7 }
    ]},
  { title: "Blue Moon", artist: "NIKI", features: [
      { category: SongFeatureCategory.ENERGY, value: 0.5 },
      { category: SongFeatureCategory.DANCEABILITY, value: 0.7 },
      { category: SongFeatureCategory.SPEECHINESS, value: 0.4 },
      { category: SongFeatureCategory.VALENCE, value: 0.7 },
      { category: SongFeatureCategory.TEMPO, value: 0.5 }
    ]},
  { title: "Oscar Winning Tears", artist: "RAYE", features: [
      { category: SongFeatureCategory.ENERGY, value: 0.4 },
      { category: SongFeatureCategory.DANCEABILITY, value: 0.8 },
      { category: SongFeatureCategory.SPEECHINESS, value: 0.6 },
      { category: SongFeatureCategory.VALENCE, value: 0.4 },
      { category: SongFeatureCategory.TEMPO, value: 0.7 }
    ]}
]);

const selectedVote = ref<number | null>(null);
const countdown = ref(90);
const isTimeUp = ref(false);
let timer: NodeJS.Timeout | null = null;

const authStore = useAuthStore();
const user = authStore.user;

const removedFromSession = ref(false);

const handleVote = (songIndex: number) => {
  if (selectedVote.value === songIndex) {
    selectedVote.value = null;
  } else {
    selectedVote.value = songIndex;
  }
  console.log(`Voted for song ${songList.value[songIndex].title}`);
};

const handleSessionMessages = (sessionMessage) => {
  switch (sessionMessage.type) {
    case SessionMessageType.GUEST_REMOVED:
      removedFromSession.value = true;
      break;
    default:
      break;
  }
};

// Countdown logic
onMounted(() => {
  timer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value -= 1;
    } else if (countdown.value === 0) {
      isTimeUp.value = true; // Show popup when countdown reaches 0

      // Automatically hide popup after 3 seconds
      setTimeout(() => {
        isTimeUp.value = false;
      }, 5000);

      clearInterval(timer);
    }
  }, 1000);

  sessionSocket.connect(props.sessionId, handleSessionMessages);

});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});
</script>

<template>
  <div v-if="removedFromSession">
    You were removed from this session.
  </div>
  <div class="mobile-visualization" v-else>
    <div class="sticky-header">
      <h2 class="header">Vote for the next song!</h2>
      <p class="countdown">Time remaining: {{ countdown }}s</p>
    </div>
    <div class="song-list">
      <div v-for="(song, index) in songList" :key="index" class="song-item">
        <Flower :features="song.features" :size="80" :circleRadius="40" />
        <div class="song-details">
          <p class="song-title">{{ song.title }}</p>
          <p class="song-artist">{{ song.artist }}</p>
        </div>
        <div class="vote-controls">
          <button
            :class="{ active: selectedVote === index }"
            @click="handleVote(index)"
          >
            <i class="pi pi-thumbs-up"></i>
          </button>
        </div>
      </div>
    </div>
    <div v-if="isTimeUp" class="popup">
      <div class="popup-content">
        <p class="line1">Time up!</p>
        <p class="line2">Your vote has been collected!</p>
      </div>
    </div>
  </div>
</template>


<style scoped>
.mobile-visualization {
  text-align: center;
  color: white;
  overflow: auto;
}

.sticky-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #272525;
}

.header {
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 5px;
}

.countdown {
  font-size: 16px;
  margin-bottom: 5px;
  color: #FFCC00;
}

.song-list {
  display: flex;
  flex-direction: column;
  padding-left: 5px;
}

.song-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 0;
}

.song-details {
  flex: 1;
  padding-left: 5px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.song-title, .song-artist {
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.vote-controls {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.vote-controls button {
  background: none;
  border: none;
  font-size: 24px;
  color: white;
  cursor: pointer;
}

.vote-controls button.active {
  color: #6AA834;
}

.popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.popup-content {
  background: #363636;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
}

.line1 {
  font-size: 18px;
  color: #FFCC00;
}

.line2 {
  font-size: 16px;
  color: #FFF;
}
</style>
