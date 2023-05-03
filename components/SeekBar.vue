<template>
  <div class="seek-bar">
    <input type="range" min="0" max="100" step="0.1" v-model="progress" @change="handleSeekChange">
    <span>{{ currentTimeFormatted }}</span>
  </div>
</template>

<script>
export default defineComponent({
  name: "SeekBar",
  data() {
    return {
      progress: 0,
      currentTime: 0,
    }
  },
  props: {
    songDuration: {
      type: Number,
      required: true,
    },
    givenTime: {
      type: Number,
      required: true,
    },
  },
  methods: {
    handleSeekChange(event) {
      let newTime = (event.target.value / 100) * this.songDuration;
      this.$emit('seek', newTime);
    },
    formatTime(timeInSec) {
      const minutes = Math.floor(timeInSec / 60);
      const seconds = Math.floor(timeInSec % 60);
      return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
    },
  },
  computed: {
    currentTimeFormatted() {
      const currentTimeInSec = this.currentTime;
      const durationInSec = this.songDuration;
      const currentTimeFormatted = this.formatTime(currentTimeInSec);
      const durationFormatted = this.formatTime(durationInSec);
      return `${currentTimeFormatted} / ${durationFormatted}`;
    }
  },
  watch: {
    progress: {
      handler(progress) {
        let newTime = (progress / 100) * this.songDuration;
        this.currentTime = newTime;
      },
    },
    givenTime: {
      handler(givenTime) {
        this.currentTime = givenTime;
        this.progress = (givenTime / this.songDuration) * 100;
      },
    },
  },
});
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
