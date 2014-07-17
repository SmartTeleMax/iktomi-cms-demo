var PopupFieldListSelect = new Class({
    Implements: [Options, Events],

    initialize: function(fieldlist, options){
        this.setOptions(options);
        this.fieldlist = fieldlist;
        this.popup = new Popup(undefined, {'empty_on_hide': false});
    },

    show: function(){
        this.drawList(this.popup);
        this.popup.show();
        this.searchField.focus();
    },

    hide: function(){
        this.drawList(this.popup);
        this.popup.hide();
        this.searchField.focus();
    },

    getOption: function(item){
      return {'value': item.getElement('[name$=.id]').value,
              'title': item.getElement('[type=text]').value}
    },
    getOptions: function(){
      return this.fieldlist.items().map(this.getOption).filter(function(x){return x.value});
    },

    filterHandler: function(e){
        var filterBy = e.target.value;
        var options = this.getOptions();
        var visibleOptions = new Hash();

        options.each(function(opt){
            var start = opt.title.toLowerCase().search(filterBy.toLowerCase())
            if (start >-1){
                visibleOptions.set(opt.value, {'title':opt.title, 'value':opt.value, 'start':start});
            }
        }.bind(this));
        this.buildSelectable(this.popup, visibleOptions, filterBy.length);
    },

    buildSelectable: function(popup, newOptions, highlightLength){
        popup.contentEl.empty();
        newOptions.each(function(opt, value){
            if(highlightLength) {
            var optTitle = opt.title.substring(0, opt.start)+
              '<b>'+opt.title.substring(opt.start, opt.start+highlightLength)+'</b>'+
              opt.title.substring(opt.start+highlightLength);
            } else {
              var optTitle = opt.title;
            }

            var newOption = new Element('div', {
                'html': optTitle,
                'data-value': opt.value,
                'class':'filter-list-value'
            });

            newOption.addEvent('click', function(e){
                var target = e.target.hasClass('filter-list-value')?
                                e.target:
                                e.target.getParent('.filter-list-value');
                this.fireEvent('change', {'value': target.dataset.value,
                                          'title': target.get('text')});
            }.bind(this));
            popup.adopt(newOption);
        }.bind(this));

        popup.onWindowResize();
    },

    drawList: function(popup){
      if(!this.searchField){

        this.searchField = new Element('input', {
              'type':'text'
            }).addEvents({
              'keydown': this.filterHandler.bind(this),
              'keyup': this.filterHandler.bind(this)
            });

        popup.setFixedContent(
          new Element('label', {
            'text':'поиск', 
            'class':'search_label'
          }).adopt(this.searchField)
        );
      }
      this.buildSelectable(popup, this.getOptions());
    }
});

