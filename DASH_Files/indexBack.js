document.addEventListener('DOMContentLoaded', function() {
    const videoElement = document.getElementById('videoPlayer');
    const player = dashjs.MediaPlayer().create();

    // Configure ABR strategy here BEFORE initialize
    player.updateSettings({
        streaming: {
            abr: { ABRStrategy: 'abrBola' },  // 👈 buffer-based ABR
            abandonLoadTimeout: 0             // keep your other config
        }
    });

    const mpdUrl = 'video_separate.mpd';
    player.initialize(videoElement, mpdUrl, true);

    // Event listeners
    player.on(dashjs.MediaPlayer.events.ERROR, function(e) {
        console.error('Dash.js Error:', e.error ? e.error.message : e);
    });

    player.on(dashjs.MediaPlayer.events.PLAYBACK_PLAYING, function() {
        console.log('▶️ Playback started successfully!');
    });

    player.on(dashjs.MediaPlayer.events.MANIFEST_LOADED, function() {
        console.log('✅ Manifest loaded successfully');
    });
});
