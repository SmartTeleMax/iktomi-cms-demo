var CheckPhotoOrder = new Class({
  Extends: PreSaveHook,

  confirm_text: 'Вы проверили сортировку фотографий?',

  get_widget: function(){
    return $(this.frm.id + '-photos_edit').retrieve('widget');
  },

  confirm_rule: function(){
    this.widget.addEvent('change', function(){
      this.require_check = false;

      var length = 0;
      this.widget._selected_items.each(function(el){
        if(el){
          length++;
        }
      });

      if(length > 1) {
        this.require_check = true;
      }
    }.bind(this))
  }
});

var CheckMainPhoto = new Class({
  Extends: PreSaveHook,

  confirm_text: 'Вы выбрали главную фотографию?',

  get_widget: function(){
    return $(this.frm.id + '-photos_edit').retrieve('widget');
  },

  confirm_rule: function(){
    this.widget.addEvent('change', function(){
      this.require_check = true;
    }.bind(this));

    this.widget.addEvent('select_main', function(){
      this.require_check = false;
    })
  }
});
