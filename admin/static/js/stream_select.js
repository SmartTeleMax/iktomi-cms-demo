var StreamSelect = new Class({
  // XXX name of class?
    Implements: [Options, Events],

    initialize: function(widget, options){
        this.setOptions(options);
        this.widget = widget;
        this.popup = new Popup();
    },

    show: function(){
        this.drawList();
        this.popup.show();
    },

    hide: function(){
        this.drawList();
        this.popup.hide();
    },

    drawList: function(){
      this.popup.contentEl.empty();
      var container = new Element('table', {'class': 'w-popup-stream-select-items'});
      container.addEvent('click', function(e){
        e.stopPropagation(); e.preventDefault();
        var row = e.target.tagName == 'TR'? e.target: e.target.getParent('tr.item');
        this.fireEvent('change', {'value': row.getElement('.field_id').get('text').trim()});
      }.bind(this), true);
      container.adopt(this.widget.getItemsDiv().clone());
      container.getElements('.w-control-cell').destroy();
      container.getElements('a').set('href', 'javascript: void(0)');
      this.popup.adopt(container);
      this.popup.onWindowResize();
    }
});

