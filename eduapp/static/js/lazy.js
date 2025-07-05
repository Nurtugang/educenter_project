function loadYouTubeModal(videoId) {
  const modalContent = document.getElementById('youtube-modal-content');
  modalContent.innerHTML = `
    <div class="modal-header">
      <h4 class="modal-title">Просмотр видеоролика</h4>
      <button type="button" class="close" data-dismiss="modal">&times;</button>
    </div>
    <div class="modal-body">
      <div class="youtube-player" style="
        position: relative;
        padding-bottom: 56.25%;
        height: 0;
        overflow: hidden;">
        <iframe style="position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
      </div>
    </div>
    <div class="modal-footer">
      <button type="button" class="btn btn-secondary" data-dismiss="modal">Закрыть</button>
    </div>
  `;

  // Show the modal
  $('#youtube-modal').modal('show');
}

// Add click event listeners to all "Load Video" buttons
const loadVideoBtns = document.querySelectorAll('.load-video-btn');
loadVideoBtns.forEach(function (btn) {
  btn.addEventListener('click', function () {
    const videoId = btn.getAttribute('data-video-id');
    loadYouTubeModal(videoId);
  });
});
