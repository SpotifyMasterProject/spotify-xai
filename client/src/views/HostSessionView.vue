<!-- Main session view for host -->
<script setup>
import { ref, computed } from "vue";
import LogoIntroScreen from "@/components/LogoIntroScreen.vue";
import SessionHistoryItem from "@/components/SessionHistoryItem.vue";
import StartBlendButton from "@/components/StartBlendButton.vue";
import PlaylistCreator from "@/components/PlaylistCreator.vue";
import RunningHostSession from "@/components/RunningHostSession.vue";
import { HostSession } from "@/types/Session";
import Sidebar from "primevue/sidebar";

// TODO: Get sessions from BE.
const sessions = [
    new HostSession({
        id: "123",
        invitationLink: "#",
        guests: [],
        playlistName: "Playlist 1",
        playlist: [],
        creationDate: Date.parse("2024-03-12 12:00:20"),
        isRunning: false 
    }),
    new HostSession({
        id: "234",
        invitationLink: "#",
        guests: [],
        playlistName: "Playlist 2",
        playlist: [],
        creationDate: Date.parse("2024-02-12 12:00:20")
    })
];

const selectedSessionIndex = ref(null);
const sessionHistoryVisible = ref(false);
const createNewSessionFlow = ref(false);

const runningSession = computed(() => {
    return sessions.find((session) => session.isRunning);
});

</script>
<template>
    <div class="session-view">
        <header class="header">
            <logo-intro-screen class="logo"/>
            <i class="settings-icon pi pi-cog" @click="sessionHistoryVisible = true"></i>
        </header>
        <div>
            <Sidebar
                v-model:visible="sessionHistoryVisible"
                :showCloseIcon="false">
                <div class="session-history-container">
                    <session-history-item
                        class="session-history"
                        v-for="session in sessions"
                        :session="session"
                        @click="(index) => selectedSessionIndex = index"
                    />
                </div>
            </Sidebar>
        </div>
        <div class="container">
            <div v-if="!createNewSessionFlow">
                <start-blend-button v-if="!runningSession" @click="createNewSessionFlow = true" />
                <running-host-session v-else />
            </div>
            <playlist-creator v-else></playlist-creator>
        </div>
    </div>
</template>

<style scoped>
.session-view {
    background-color: var(--backcore-color1);
    height: 100vh;
    display: flex;
    flex-direction: column;
}
.header {
    margin-top: 30px;
    display: flex;
    flex-direction: row;
}

.logo {
    margin: 0 auto;
}

.settings-icon {
    position: absolute;
    right: 30px;
    color: var(--logo-highlight-color);
    font-size: 30px;
    cursor: pointer;
}

.container {
    margin-top: 50px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.session-history-container {
    background-color: var(--backcore-color2);
    padding-top: 20px;
    height: 100vh;
    position: relative;
}
</style>
