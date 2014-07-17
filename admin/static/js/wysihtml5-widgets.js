(function(wysihtml5) {
  var LinkPlugin = {

      getWidget: function(formId){
          var fieldlist = $(formId + '-' + this.widgetName).retrieve('widget');
          return new PopupFieldListSelect(fieldlist);
      },

      _init: function(composer){
        var textarea = composer.textarea.element;
        if (! textarea.retrieve(this.widgetName)){
          var widget = this.getWidget(textarea.getParent('form').id);

          widget.addEvent('change', function(e){
            composer.commands.exec(this.commandName, e.value)
          }.bind(this));
          textarea.store(this.widgetName, widget);
        }
        return textarea.retrieve(this.widgetName);
      },

      tagName: 'ASIDE',
      widgetName: 'link_blocks', 
      commandName: 'doclink',
      // XXX show front version from front widget
      url: '/docs/admin/ru/doc-link-block/ID',

      exec: function(composer, command, value) {
        //var dropdown = this._init(composer);
        //var stream_select = dropdown.retrieve('widget');
        var widget = this._init(composer);
        if (!value){
          //dropdown.setStyle('display', dropdown.style.display == 'none'? '': 'none');
        } else if(value == 'select'){
          widget.show();
        } else {
          var aside = this.createElement(value);
          insertBlock(composer, aside);
          widget.hide();
        }
      },

      createElement: function(value){
        var aside = new Element(this.tagName, {
          'item_id': value,
          'data-align': 'center'
        });
        return this.prepareElement(aside);
      },

      bindBodyEvents: function(win){
        if (!win.boundLinkPluginEvents){
          win.boundLinkPluginEvents = true;
          var body = win.document.body;
          body.addEventListener('click', function(e){
            var tgt = e.target;
            var aside = tgt.parentNode;
            if (tgt.classList.contains('remove')){
              aside.parentNode.removeChild(aside);
            } else if (tgt.classList.contains('move-up')){
              if(aside.previousElementSibling) {
                // XXX delegate all events to body!
                aside.parentNode.insertBefore(aside, aside.previousElementSibling);
              }
            } else if (tgt.classList.contains('move-up')){
              if(aside.previousElementSibling) {
                // XXX delegate all events to body!
                aside.parentNode.insertBefore(aside, aside.previousElementSibling);
              }
            } else if (tgt.classList.contains('move-down')){
              if(aside.nextElementSibling) {
                // XXX delegate all events to body!
                aside.parentNode.insertBefore(aside, aside.nextElementSibling.nextElementSibling);
              }
            } else if (tgt.classList.contains('move-left')){
              aside.dataset.align = 'left';
            } else if (tgt.classList.contains('move-right')){
              aside.dataset.align = 'right';
            } else if (tgt.classList.contains('move-center')){
              aside.dataset.align = 'center';
            }
          });
        }
      },

      prepareElement: function(aside){
        var value = aside.getAttribute('item_id');
        aside.setAttribute('contenteditable', 'false');
        var win = aside.ownerDocument.defaultView;
        this.bindBodyEvents(win);

        if (!aside.querySelector('iframe')){
          if (!aside.getAttribute('data-align')){
            aside.setAttribute('data-align', 'center');
          }
          var iframe = new Element('iframe', {'src': this.url.replace('ID', value) });
          iframe.addEventListener('load', function(){
            var height = iframe.contentWindow.document.body.scrollHeight + 'px'
            if (win.composer){
              win.composer.withNoHistory(function(){
                iframe.style.height = height;
              });
            } else {
              iframe.style.height = height;
            }
          }, false);
          aside.innerHTML = '';
          aside.appendChild(iframe);

          aside.classList.add('replaceble-block');

          if (win.composer){
            var rmBtn = win.document.createElement('button');
            rmBtn.className = 'remove';
            aside.appendChild(rmBtn);

            var upBtn = win.document.createElement('button');
            upBtn.className = 'move-up';
            aside.appendChild(upBtn);

            var downBtn = win.document.createElement('button');
            downBtn.className = 'move-down';
            aside.appendChild(downBtn);

            if (0){
              var leftBtn = win.document.createElement('button');
              leftBtn.className = 'move-left';
              aside.appendChild(leftBtn);

              var rightBtn = win.document.createElement('button');
              rightBtn.className = 'move-right';
              aside.appendChild(rightBtn);

              var centerBtn = win.document.createElement('button');
              centerBtn.className = 'move-center';
              aside.appendChild(centerBtn);
            }
          }
        }
        return aside;
      }
  };

  var InlineLinkPlugin = Object.append(
    Object.create(wysihtml5.commands.PopupStreamSelectPlugin), {
      tagName: 'A',
      createElement: function(value){
        return new Element(this.tagName, {'href': 'model://'+this.propertyName + "/" + value});
      },

      elementMatches: function(el){
        var href = el && el.getAttribute('href');
        return href &&
               href.substr(0, 8) == 'model://' &&
               href.split('/')[2] == this.propertyName &&
               href.split('/')[3] &&
               href.split('/')[4] === undefined;
      }
    });





  wysihtml5.commands.objectLink = {
    exec: function(composer, command, value) {
      var dropdown = composer.textarea.element
                             .getParent('.wysihtml5-widget')
                             .getElement('[data-wysihtml5-dialog="ObjectLink"]');
      dropdown.setStyle('display', dropdown.style.display == 'none'? '': 'none');
    }
  }


  function replaceBlocks(element){
    for (var cmd in wysihtml5.commands) if (wysihtml5.commands.hasOwnProperty(cmd)){
      cmd = wysihtml5.commands[cmd];
      if (cmd.prepareElement){
        var tag = cmd.tagName.toLowerCase();
        var asides = element.querySelectorAll(tag); // XXX crossbrowser?
        for (var i=asides.length; i--;){
          cmd.prepareElement(asides[i]);
        }
      }
    }
  }
  window.replaceDocBlocks = replaceBlocks;


  function insertBlock(composer, block){
    var range = composer.selection.getRange().nativeRange;
    range.splitBoundaries();
    var place = range.startContainer;
    if (place.tagName == 'BODY') { place = place.firstChild; }
    while (place.parentNode.tagName != 'BODY') {
      place = place.parentNode
    }
    place.parentNode.insertBefore(block, place.nextSibling);

    var isLast = true, last = block.nextSibling;
    while (last) { 
      if (last.textContent.trim()){ isLast = false; break; }
      last = last.nextSibling;
    }
    if (isLast) {
      var p = new Element('p', {'html': '&nbsp;'});
      place.parentNode.insertBefore(p, block.nextSibling);
    }
  }


  var DocLinkPlugin = Object.append(
    Object.create(LinkPlugin), {
      tagName: 'IKTOMI_DOCLINK',
      widgetName: 'link_blocks', 
      commandName: 'doclink',
      // XXX show front version from front widget
      url: '/docs/admin/ru/doc-link-block/ID',
      getWidget: function(formId){
          var fieldlist = $(formId + '-' + this.widgetName).retrieve('widget');
          return new PopupFieldListSelect(fieldlist);
      }
  });
  wysihtml5.commands.doclink = DocLinkPlugin;

  var PhotoLinkPlugin = Object.append(
    Object.create(LinkPlugin), {
      tagName: 'IKTOMI_PHOTO',
      widgetName: 'photos',
      commandName: 'photolink',
      // XXX show front version from front widget
      url: '/docs/admin/ru/photo-block/ID',
      getWidget: function(formId){
        var pss = $(formId + '-' + this.widgetName).retrieve('widget');
        return new StreamSelect(pss);
      }
  });

  wysihtml5.commands.photolink = PhotoLinkPlugin;


  var PhotoSetLinkPlugin = Object.append(
    Object.create(LinkPlugin), {
      tagName: 'IKTOMI_PHOTOSET',
      widgetName: 'photo_sets',
      commandName: 'photosetlink',
      // XXX show front version from front widget
      url: '/docs/admin/ru/photo-set-block/ID',
      getWidget: function(formId){
        var pss = $(formId + '-' + this.widgetName).retrieve('widget');
        return new StreamSelect(pss);
      }
  });
  wysihtml5.commands.photosetlink = PhotoSetLinkPlugin;

  function makeInlineLinkPlugin(name){
    return Object.append(
        Object.create(InlineLinkPlugin), {
          propertyName: name,
          commandName:  name + 'Link',
          streamName:   name + 's'
      });
  }

  wysihtml5.commands.termLink = makeInlineLinkPlugin('term');
  wysihtml5.commands.docLink = makeInlineLinkPlugin('doc');


  // XXX hack!
  var setValue = wysihtml5.views.Composer.prototype.setValue;
  wysihtml5.views.Composer.prototype.setValue = function(){
    result = setValue.apply(this, arguments);
    this.withNoHistory(function(){
      replaceBlocks(this.element);
    });
    return result;
  }

  var _create = wysihtml5.views.Composer.prototype._create;
  wysihtml5.views.Composer.prototype._create = function(){
    result = _create.apply(this, arguments);
    this.element.ownerDocument.defaultView.composer = this;
    this.withNoHistory(function(){
      replaceBlocks(this.element);
    });
    return result;
  }


  wysihtml5.commands.createLinkAdvanced = Object.append(
    Object.create(wysihtml5.commands.createLink), {
      exec: function(composer, command, value) {
        wysihtml5.commands.createLink.exec.call(this, composer, command, value);
        var panel = composer.parent.toolbar.container;
        panel.getElements('.create-link-dialog').removeClass('more');
      }
    });

  wysihtml5.commands.unlinkAdvanced = Object.append(
    Object.create(wysihtml5.commands.unlink), {
      createCommand: wysihtml5.commands.createLinkAdvanced
    });

  wysihtml5.commands.typography = {
    exec: function(composer, command, value) {
      var value = composer.getValue();
      value = richtypo.richtypo(value, ['cleanup_before', 'save_tags', 'quotes', 'lite', 'spaces_lite', 'spaces', 'restore_tags'], 'ru');
      composer.setValue(value);
    }
  }

})(wysihtml5);

