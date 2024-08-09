<template>
  <div class="song-table-container">
    <div class="song-table">
      <table>
        <thead>
          <tr>
            <th class="icon-header"></th>  <!-- Empty for the icon -->
            <th>Track Name</th>
            <th>Album</th>
            <th>Artists</th>
            <th>Danceability</th>
            <th>Energy</th>
            <th>Speechiness</th>
            <th>Valence</th>
            <th>Tempo</th>
            <th>Popularity</th>
            <th>Release Date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="song in songs" :key="song.id">
            <td class="icon-cell">
              <img src="../assets/table-play-icon.png" alt="play-icon" class="song-icon">
            </td>
            <td>{{ song.track_name }}</td>
            <td>{{ song.album }}</td>
            <td>{{ song.artists }}</td>
            <td>{{ song.danceability }}</td>
            <td>{{ song.energy }}</td>
            <td>{{ song.speechiness }}</td>
            <td>{{ song.valence }}</td>
            <td>{{ song.tempo }}</td>
            <td>{{ song.popularity }}</td>
            <td>{{song.release_date}}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { songs } from '@/types/Song';

</script>

<style scoped>
.song-table-container {
  background-color: #363636;
  padding: 5px 0px 5px 0px;
  border-radius: 15px;
  overflow: hidden;
}

.song-table {
  width: 100%;
  color: #D9D9D9;
  overflow: hidden;
}

.song-table table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 15px;
  table-layout: fixed;
  overflow: hidden;
}
.song-table th, .song-table td {
  padding: 8px;
  text-align: center;
  word-wrap: break-word;
  border-bottom: 1px solid transparent;
  color: #D9D9D9;
}

.song-table th.icon-header, .song-table td.icon-cell {
  width: 20px;
  text-align: center;
}

.song-table img.song-icon {
  width: 20px;
  height: 20px;
  vertical-align: middle;
}
</style>