$('#create').click(function() {
  word = $('input').val();
  window.location.href = '/create/' + word;
  return false;
});

$('#export').click(function() {
  $.get('export')
    .done(function(data) {
      alert('Exported cards to: ' + data);
    })
    .fail(function() {
      alert('Export failed');
    });
});
