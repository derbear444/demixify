<template>
  <div class="seek-bar">
    <input type="range" min="0" max="100" step="1" v-model="progress">
    <span>{{ currentTime }}</span>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import * as Tone from "tone";

export default {
  name: "SeekBar",
  setup() {
    const progress = ref(0);

    const currentTime = computed(() => {
      const currentTimeInSec = Tone.Transport.seconds;
      const durationInSec = Tone.Transport.loopEnd;
      const currentTimeFormatted = formatTime(currentTimeInSec);
      const durationFormatted = formatTime(durationInSec);
      return `${currentTimeFormatted} / ${durationFormatted}`;
    });

    function formatTime(timeInSec) {
      const minutes = Math.floor(timeInSec / 60);
      const seconds = Math.floor(timeInSec % 60);
      return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
    }

    onMounted(() => {
      setInterval(() => {
        progress.value = (Tone.Transport.seconds / Tone.Transport.loopEnd) * 100;
      }, 1000);
    });

    return {
      progress,
      currentTime,
    };
  },
};
</script>

<style scoped>
.seek-bar {
  display: flex;
  align-items: center;
}

.seek-bar input {
  width: 100%;
  margin-right: 1rem;
}

.seek-bar span {
  font-size: 0.8rem;
}
</style>