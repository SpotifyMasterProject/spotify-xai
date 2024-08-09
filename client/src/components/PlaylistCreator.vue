<script setup>
import { ref, computed } from 'vue';
import InputText from 'primevue/inputtext';
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';
import { Song } from '@/types/Song';

// TODO: Get from BE.
const songs = ref([
    new Song({
        id: "123",
        name: "Cruel Summer",
        artists: ["Taylor Swift"]
    }),
     new Song({
        id: "234",
        name: "Cruel Summer1",
        artists: ["Taylor Swift"]
    }),
    new Song({
        id: "345",
        name: "Cruel Summer2",
        artists: ["Taylor Swift"]
    }),
     new Song({
        id: "456",
        name: "Cruel Summer3",
        artists: ["Taylor Swift"]
    }),
    new Song({
        id: "567",
        name: "Not Like Us",
        artists: ["Kendrick Lamar"]
    }),
    new Song({
        id: "678",
        name: "Too Sweet",
        artists: ["Hozier"]
    }),
     new Song({
        id: "789",
        name: "Guess",
        artists: ["Charli xcx", "Billie Eilish"]
    }),
]);

const title = ref();
const filteredSongs = ref();
const selectedSong = ref();
const selectedSongs = ref([]);

// Combines the artists into a single string.
const combineArtists = (artists) => {
    return artists.join(', ');
};

// Compute the songs not already selected.
const notSelectedSongs = computed(() => {
    const selectedSongsIds = selectedSongs.value.map((song) => song.id);
    return songs.value.filter((song) => !selectedSongsIds.includes(song.id));
});

// True, if the session can be started.
// Currently, if the user selected at least 3 songs and a title.
const canStartSession = computed(() => {
    return selectedSongs.value.length >= 3 && title.value;
});

// Function which is executed by the autocomplete component,
// which filters the songs, based on the user query.
const search = (event) => {
    if (!event.query.trim().length) {
        filteredSongs.value = [...notSelectedSongs.value];
    } else {
        filteredSongs.value = notSelectedSongs.value.filter((song) => {
            const query = event.query.toLowerCase();
            return song.name.toLowerCase().startsWith(query) ||
                combineArtists(song.artists).toLowerCase().startsWith(query);
        });
    }
};

// Selects a song from the autocomplete options and adds it to the
// selected song list.
const selectSong = (event) => {
    selectedSongs.value = [...selectedSongs.value, selectedSong.value];
    selectedSong.value = null;
}

// Removes a song from the selected list.
const removeSong = (songToRemove) => {
    selectedSongs.value = selectedSongs.value.filter(song => song.id !== songToRemove.id);
};

const startSession = () => {
    // TODO: Call BE with the selected songs.
    console.log("Start Session");
};

</script>

<template>
    <div class="playlist-creator">
        <InputText
            class="title"
            type="text"
            v-model="title"
            placeholder="Playlist Title..." />
        <div class="songs">
            <h2 class="songs-header">Add 3 songs to start the blend</h2>
            <AutoComplete
                class="search" v-model="selectedSong"
                @option-select="selectSong"
                :suggestions="filteredSongs"
                @complete="search"
                variant="filled"
                :unstyled="false"
                overlayClass="overlay"
                placeholder="Search">
                <template #option="slotProps">
                    <div class="song">
                        <i class="pi pi-play"></i>
                        <div class="song-details">
                            <span class="song-title">{{ slotProps.option.name }}</span>
                            <span class="song-artists">{{ combineArtists(slotProps.option.artists) }}</span>
                        </div>
                    </div>
                </template>
            </AutoComplete>
            <div class="selected-songs">
                <!-- TODO: Consider reusing the same component as the autocomplete item. -->
                <div class="selected-song" v-for="song in selectedSongs">
                    <i class="pi pi-play"></i>
                    <div class="song-details">
                        <span class="song-title">{{ song.name }}</span>
                        <span class="song-artists">{{ combineArtists(song.artists) }}</span>
                    </div>
                    <i class="pi pi-trash delete-icon" @click="removeSong(song)"></i>
                </div>
            </div>
        </div>
        <Button
            class="start-session"
            :disabled="!canStartSession"
            @click="startSession">
            Start
        </Button>
    </div>
</template>

<style>

.playlist-creator {
    --margin-inline: 20px;
    background-color: var(--backcore-color3);
    width: min(700px, 90vw);
    height: min(600px, 60vh);
    display: flex;
    flex-direction: column;
    gap: 8px;
    border-radius: 20px;
    position: relative;
}

.title {
    margin: var(--margin-inline) 32px 5px;
    width: 70%;
    font-weight: 700;
    font-size: 25px;
    border: none;
}
.songs {
  background-color: var(--backcore-color1);
  height: 100%;
  margin: 10px var(--margin-inline) 80px;
  padding-inline: var(--margin-inline);
  border-radius: 15px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.songs-header {
  color: var(--font-color);
}

.search.p-autocomplete {
  display: block;
  background-color: var(--backcore-color2);
  border-radius: 15px;
  font-size: 16px;
  border: solid;
  border-color: var(--backcore-color3); 
  border-width: 2px;    
  padding: 5px 10px;
  box-sizing: border-box;
}

.title, .songs input {
  background-color: var(--backcore-color3);
  font-family: inherit;
  color: var(--font-color);
}

input:focus {
    outline: none;
}

.songs .search.p-autocomplete ::placeholder {
    color: var(--backcore-color3);
}

.p-autocomplete-overlay.overlay {
    margin-top: 10px;
    background-color: var(--backcore-color3);
    color: var(--font-color);
    font-family: inherit;
    border-radius: 10px;
    overflow-y: auto;
    padding: 5px;
    width: 30%;
}

.selected-song {
    display: flex;
    flex-direction: row;
    justify-content: start;
    align-items: center;
    gap: 8px;
    color: var(--font-color);
    border-radius: 5px;
    padding: 5px;
}

.search .p-autocomplete-loader {
  color: var(--font-color);
}

.p-autocomplete-overlay.overlay .song {
    display: flex;
    flex-direction: row;
    justify-content: start;
    align-items: center;
    gap: 8px;
    color: var(--font-color);
    border-radius: 5px;
    padding: 5px;
    margin-inline: 5px;
    width: 100%;
}

.p-autocomplete-overlay.overlay .song-details, .song-details {
    display: flex;
    flex-direction: column;
    justify-content: start;
    gap: 2px;
}

.overlay .p-autocomplete-list {
    gap: 7px;
}

.p-autocomplete-overlay.overlay .song:hover {
    background-color: var(--backcore-color1);
}

.p-autocomplete-overlay.overlay .song-title, .song-title {
    font-weight: bold;
}

.p-autocomplete-overlay.overlay .song-artists, .song-artists {
    font-size: 12px;
}

.selected-songs {
    overflow-y: auto;
    max-height: 70%;
}

.selected-songs .selected-song .delete-icon {
    color: var(--font-color); 
    cursor: pointer; 
    margin-left: auto;
    padding-right: 10px;
}

.selected-songs .selected-song .delete-icon:hover {
    color: red; 
}
.start-session {
    position: absolute;
    bottom: 20px;
    right: var(--margin-inline);
    font-size: 16px;
    background-color: var(--logo-highlight-color);
    border-radius: 12px;
    border: none;
    padding: 8px 20px;
    cursor: pointer;
    font-weight: bold;
}
</style>
