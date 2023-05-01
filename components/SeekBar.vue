<template>
  <div>
    <div class="relative flex items-center">
      <div class="h-1 w-full bg-gray-600 rounded-full">
        <div class="absolute h-1 top-0 bg-green-500 rounded-full" :style="{ width: `${progress}%` }"></div>
        <input class="appearance-none w-full h-full rounded-full focus:outline-none" type="range" min="0.0" max="100.0"
          step="0.1" v-model.number="progress" @mousedown="isDragging = true" @mousemove="updateProgress"
          @mouseup="isDragging = false" />
      </div>
    </div>
  </div>
</template>
  
<script>
export default {
  data() {
    return {
      isDragging: false,
      progress: 0,
    };
  },
  methods: {
    updateProgress(event) {
      if (this.isDragging) {
        const width = event.target.clientWidth;
        const clickX = event.offsetX;
        const percent = clickX / width;
        const newPosition = percent * 100;
        this.progress = newPosition;
        this.$emit('seek', newPosition);
      }
    },
  },
};
</script> 