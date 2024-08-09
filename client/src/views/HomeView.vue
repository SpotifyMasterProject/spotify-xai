<script setup lang="ts">
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";
import Navigation from "@/components/Navigation.vue";
import Flower from "@/components/Flower.vue";
import PreviouslyPlayed from "@/components/PreviouslyPlayed.vue";
import SearchSongInSession from "@/components/SearchSongInSession.vue";
import { songs } from "@/types/Song";
import { ref, onMounted } from "vue";
// import { Song } from '@/types/Song';
// import axios from 'axios';

// const songs = ref<Song[]>([]);

const showPreviouslyPlayed = ref(false);


const toggleVisibility = () => {
  showPreviouslyPlayed.value = !showPreviouslyPlayed.value;
};

const flowerData = [
  { value: 0.4, color: "#144550" },
  { value: 0.6, color: "#31431E" },
  { value: 0.5, color: "#EEE8C4" },
  { value: 0.7, color: "#E4832E" },
  { value: 0.3, color: "#BB7DEC" },
];


/* function to fetch songs from backend */
// const fetchSongs = async () => {
//   try {
//     const response = await axios.get<{ data: any[]>('http://localhost:8000/getPlayList');
//     songs.value = response.data.map(songData => new Song(songData));
//   } catch (e) {
//     console.error('Failed to fetch playlist:', e);
//   }
// }

// onMounted(fetchSongs)
</script>

<template>
  <div class="type2">
    <header>
      <div class="search-bar-background">
        <input class="search-bar" type="text" placeholder="Search"/>
      </div>
      <div class="logo-nav-container">
        <logo-intro-screen />
        <nav>
          <Navigation />
        </nav>
      </div>
    </header>
    <div class="middle" :class="{ expanded: !showPreviouslyPlayed }">
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
      <Flower :features="flowerData" :size="300" :circleRadius="100" />
    </div>
    <div
      class="previously-played"
      :class="{ minimized: !showPreviouslyPlayed }"
    >
      <div class="header-container">
        <h3>Previously Played</h3>
        <button
          class="text-sm rounded min-h-[32px] px-3 py-0.5 font-semibold hover:bg-gray-800"
          @click="toggleVisibility"
        >
          {{ showPreviouslyPlayed ? "Hide" : "Show" }}
        </button>
      </div>
      <div v-show="showPreviouslyPlayed">
        <PreviouslyPlayed :songs="songs"></PreviouslyPlayed>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
