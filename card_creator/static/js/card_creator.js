var Modes = {
  PICK_SENTENCES: 0,
  CREATE_CARDS: 1,
};

var data = {
  word: word,
  definitions: [],
  pickedDefinitions: [],
  examples: [],
  pickedExamples: [],
  mode: Modes.PICK_SENTENCES,
  cards: [],
  pendingSentence: '',
};

function DefinitionString(def) {
  return '(' + def.pinyin_diacritic + ') ' + def.meaning;
}

function BlankOutExample(example, word) {
  return example.replace(word, '___');
}

var app = new Vue({
  el: '#app',
  data: data,
  created: function() {
    $.getJSON('/api/lookup/' + data.word).done(function(recvd) {
      data.definitions = recvd.definitions;
      data.examples = recvd.examples;
    });
  },
  methods: {
    addPendingSentence: function(event) {
      data.examples.push({
	'chinese': data.pendingSentence,
	'english': '[ADDED]',
      });
      data.pendingSentence = '';
    },
    createCards: function(event) {
      // Verify that we actually picked something.
      var definitions = [];
      for (var i = 0; i < data.pickedDefinitions.length; ++i) {
	if (data.pickedDefinitions[i]) {
	  definitions.push(data.definitions[i]);
	}
      }
      var examples = [];
      for (var i = 0; i < data.pickedExamples.length; ++i) {
	if (data.pickedExamples[i]) {
	  examples.push(data.examples[i]);
	}
      }
      if (definitions.length == 0 || examples.length == 0) {
	alert('Pick some definitions and examples!');
	return;
      }

      // Create cards.
      var info = DefinitionString(definitions[0]);
      for (var i = 1; i< definitions.length; ++i) {
	info += '<br>' + DefinitionString(definition[i]);
      }
      for (var i = 0; i < examples.length; ++i) {
	var card = {
	  frontExample: BlankOutExample(examples[i].chinese, data.word),
	  frontHints: '',
	  backWord: data.word,
	  sentence: examples[i].chinese,
	  info: info,
	  twoCards: '',
	}
	data.cards.push(card);
      }

      // Just make the first card the "back reference".
      data.cards[0].twoCards = 'Y';

      data.mode = Modes.CREATE_CARDS;
    },
    outputCards: function(event) {
      $.ajax({
	type: 'POST',
	contentType: 'application/json; charset=utf-8',
	url: '/api/add_cards',
	data: JSON.stringify(data.cards),
	dataType: 'json'
      }).done(function() {
	// Redirect to home.
	window.location.replace('/');
      });
    },
  },
})
