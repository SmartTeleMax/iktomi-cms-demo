//var PopupStreamSelectPhotos = new Class({
//  Extends: PopupStreamSelectMultiple,
//
//  _addOrderButtons: function(row) {
//      var img = row.getElement('img');
//      var img_td = img? img.getParent('td') : row.getElement('td');
//      this._createOrderButtons(row).inject(img_td, 'after');
//  },
//
//  _addControls: function(row) {
//    var first = row.getFirst();
//
//    if(first && !first.hasClass('select_main')){
//      /*row.getElements('.first').removeClass('first');*/
//      var main = new Element('td', {'class':'first select_main'});
//      var selected_value = this.container.getParent('form').getElement('[type="hidden"][name="index_photo"]');
//      var attrs = {'type': 'radio',
//                   'name': 'index_photo',
//                   'class': 'index_photo',
//                   'value': row.getElement('a[data-id]').dataset.id };
//
//      if(selected_value!=null && attrs['value']==selected_value.get('value')){
//        attrs['checked']='checked';
//        selected_value.destroy();
//      }
//      var input = new Element('input', attrs).addEvent('change', function(el){
//        this.fireEvent('change');
//        this.fireEvent('select_main');
//      }.bind(this));
//
//      main.adopt(input).inject(first, 'before');
//    }
//    this.parent(row);
//  }
//});
//
//Blocks.register('popup-stream-select-photos', function(el){
//    new PopupStreamSelectPhotos(!!el.dataset.readonly,
//                                JSON.parse(el.dataset.config));
//});
