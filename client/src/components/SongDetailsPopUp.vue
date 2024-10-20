<template>
  <div class="song-detail-modal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ song.trackName }}</h3>
      </div>
      <p><strong>Artist: </strong> {{ song.artists.join(', ') }}</p>
      <p><strong>Album: </strong> {{ song.album }}</p>
      <p><strong>Release Date: </strong> {{ formattedReleaseDate }}</p>
      <p><strong>Duration: </strong> {{ formattedDuration }}</p>
      <p><strong>Genre: </strong> {{ song.genre }}</p>
      <p><strong>Popularity: </strong> {{ song.popularity }}/100 </p>
    </div>
  </div>
</template>

<script setup>
import { Song } from '@/types/Song.ts';

const props = defineProps({
  song: {
    type: Object,
    required: true
  },
});

// Format duration from milliseconds to minute:second format
const formatDuration = (durationMs) => {
  const minutes = Math.floor(durationMs / 60000);
  const seconds = Math.floor((durationMs % 60000) / 1000);
  return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
};

// Format release date to 'YYYY-MM-DD' format
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
};

// Computed properties for formatted values
const formattedDuration = formatDuration(props.song.durationMs);
const formattedReleaseDate = formatDate(props.song.releaseDate);

console.log("song info", props.song)
</script>

<style scoped>
.song-detail-modal {
  position: fixed;
  top: 25%;
  left: 85%;
  transform: translate(-50%, -50%);
  background-color: #272525;
  border-radius: 15px;
  padding: 10px;
  z-index: 1001;
  width: 70%;
  max-width: 250px;
  color: #D9D9D9;
  border: 2px solid #6AA834;
}

.modal-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0px 8px 0px;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  word-wrap: break-word;
}

p {
  margin: 0;
  font-size: 16px;
}

@media (max-width: 600px) {
  .song-detail-modal {
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 70%;
    padding: 15px;
  }

  .modal-header h3 {
    font-size: 16px;
  }

  p {
    font-size: 14px;
  }

  .modal-header button {
    font-size: 18px;
  }
}
</style>