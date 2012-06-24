var root;
var rootNode;
var selectedNode;
var converter = new Markdown.Converter().makeHtml;
var controller;
var updated;

var Item = Backbone.Model.extend({
    idAttribute: '_id',
    url: function() {
        if (this.id) return '/nodes/' + this.id;
        else return '/nodes/new';
    },
    initialize: function() {
        if (this.id) this.set('_id_', this.get('_id').split('/').join('__'));
        if (!this.get('items')) this.set({'items': new Items()});
        else this.set({'items': new Items(this.get('items'))});
        if (!this.get('type')) this.set({'type': 'note'});
    },
    parse: function(response) {
        if (response['items']) response['items'] = new Items(response['items']);
        //console.log("RESPONSE: ");
        //console.log(response);
        return response;
    },
});

var Items = Backbone.Collection.extend({
    model: Item,
});

var NodeView = Backbone.View.extend({
    events: {
        'submit .new_child': 'addChild',
        'click .name': 'select',
        'click .add': 'doShowForm',
        'blur input': 'hideForm',
        'click input': 'absorb',
    },
    initialize: function(options) {
        _.bindAll(this);
        var classes = 'node';
        if (options.classes) classes += ' ' + options.classes;
        if (this.model.get('type')) classes += ' ' + this.model.get('type');
        console.log("Creating NodeView: " + this.model.id + ' / ' + this.model.id);
        this.el = h(
            'div',
            {class: classes, id: 'node_'+this.model.id},
            [
                h('div', {class: 'actions'}, [
                    h('a', {class: 'add'}, '+'),
                ]),
                h('div', {class: 'name'}),
                h('div', {class: 'children'}),
                h('form', {class: 'new_child'}, [
                    h('input', {name: 'name', type: 'text', placeholder: 'Add child...'}),
                ]),
            ]
        );
        this.$el = $(this.el);
        this.$name = this.$('.name');
        this.$new_child = this.$('.new_child');
        this.$children = this.$('.children');
        this.children_view = new ItemsView({el: this.$children, collection: this.model.get('items')});
        this.model.bind('change', this.render);
    },
    absorb: function(e) { e.preventDefault(); e.stopPropagation(); },
    render: function() {
        this.$name.text(this.model.get('name'));
        this.children_view.render();
        return this;
    },
    addChild: function(e) {
        e.preventDefault();
        e.stopPropagation();
        var self = this;
        var new_name = this.$new_child.children('input[name="name"]').val().trim();
        this.$new_child.children('input[name="name"]').val('');
        if (new_name == '') return;
        var new_type = false;
        if (new_name.indexOf('#')==0) {
            new_name = new_name.slice(1).trim();
            new_type = 'topic';
        }
        var new_item = new Item({name: new_name, from_: this.model.id});
        if (new_type) new_item.set('type', new_type);
        new_item.save(null, {success: function() {
            
            self.model.get('items').add(new_item);
        }});
    },
    select: function(e) {
        e.preventDefault();
        e.stopPropagation();
        controller.selectNode(this.model.id);
    },
    doShowForm: function(e) { e.preventDefault(); e.stopPropagation(); this.showForm(); },
    showForm: function() {
        this.children_view.scrollDown();
        this.$new_child.show();
        this.$new_child.children('input').focus();
    },
    hideForm: function() {
        this.$new_child.hide();
    },
});

var ItemView = Backbone.View.extend({
    events: {
        'click .delete': 'clear',
        'click .reply': 'reply',
        'click .toggle': 'toggleTopic',
        'dblclick .content': 'edit',
        'submit .new_child': 'addChild',
        'click input': 'absorb',
        'blur input': 'hideForm',
    },
    initialize: function(options) {
        _.bindAll(this);
        if (options.classes) this.classes = options.classes;
        console.log("Creating ItemView: " + this.model.id + ' / ' + this.model.id);
        this.el = h(
            'div',
            {id: 'item_'+this.model.id},
            [
                h('div', {class: 'actions'}, [
                    h('a', {class: 'reply', href:'#'}, 'r'),
                    h('a', {class: 'toggle', href:'#'}, 't'),
                    h('a', {class: 'delete', href:'#'}, 'x'),
                ]),
                h('div', {class: 'attrs'}),
                h('div', {class: 'content'}),
                h('form', {class: 'content_edit'}),
                h('div', {class: 'children'}),
                h('form', {class: 'new_child'}, [
                    h('input', {name: 'name', type: 'text', placeholder: 'Add child...'}),
                ]),
            ]
        );
        this.$el = $(this.el);
        this.$attrs = this.$('.attrs');
        this.$content = this.$('.content');
        this.$content_edit = this.$('.content_edit');
        this.$children = this.$('.children');
        this.$new_child = this.$('.new_child');
        this.children_view = new ItemsView({el: this.$children, collection: this.model.get('items')});
        this.model.bind('change', this.render);
    },
    absorb: function(e) { e.preventDefault(); e.stopPropagation(); },
    render: function() {
        var classes = 'item';
        if (this.classes) classes += ' ' + this.classes;
        if (this.model.get('type')) classes += ' ' + this.model.get('type');
        this.$el.removeClass();
        this.$el.addClass(classes);
        if (this.model.get('type')=='topic' || this.model.get('type')=='collection') {
            var name_a = h('a', {href: '#nodes/'+this.model.id}, '# '+ this.model.get('name'));
            this.$content.empty();
            this.$content.append(name_a);
            this.$children.hide();
        } else if (this.model.get('type')=='resource') {
            var name_a = h('a', {href: '#nodes/' + this.model.id}, '@ '+ this.model.get('name'));
            this.$content.empty();
            this.$content.append(name_a);
            this.$children.hide();
        } else {
            this.$content.html(converter(this.model.get('name')));
            this.$children.show();
            this.children_view.render();
        }
        this.$attrs.empty();
        if (this.model.get('kind')=='track') {
            this.$attrs.append(
                $('<span/>').html("&hearts; " + this.model.get('favoritings_count')).addClass('favoritings'),
                $('<span/>').html("&#9654; " + this.model.get('playback_count')).addClass('plays')
            );
        }
        if (this.model.get('kind')=='user') {
            this.$attrs.append(
                $('<span/>').html("&larr; " + this.model.get('followers_count')).addClass('followers')
            );
        }
        updated = this.model;
        return this;
    },
    edit: function(e) {
        this.absorb(e);
        var self = this;
        var $content_input = $(h('input', {name: 'name', type: 'text', value: this.model.get('name')}));
        this.$content_edit.submit(function(e) {
            e.preventDefault();
            var new_params = {}
            var new_name = $content_input.val().trim();
            if (new_name == '') return self.unedit();
            var new_type = false;
            if (new_name.indexOf('#')==0) {
                new_name = new_name.slice(1).trim();
                new_type = 'topic';
            }
            new_params.name = new_name;
            if (new_type) new_params.type = new_type;
            self.model.save(new_params);
            self.unedit();
        });
        $content_input.blur(function() {
            self.unedit();
        });
        this.$content_edit.empty();
        this.$content_edit.append($content_input);
        this.$content.hide();
        this.$content_edit.show();
        $content_input.focus();
    },
    unedit: function(e) {
        this.$content_edit.hide();
        this.$content.show();
    },
    toggleTopic: function(e) {
        this.absorb(e);
        var self = this;
        var old_type = this.model.get('type');
        if (old_type=='topic') this.model.save({type: 'note'});
        else this.model.save({type: 'topic'});
    },
    update: function() {
        this.model.fetch();
    },
    clear: function(e) {
        this.absorb(e);
        this.model.destroy();
    },
    remove: function() {
        $(this.el).remove();
    },
    reply: function(e) {
        this.absorb(e);
        this.$new_child.show();
        this.$new_child.children('input').focus();
    },
    addChild: function(e) {
        this.absorb(e);
        var self = this;
        var new_name = this.$new_child.children('input[name="name"]').val().trim();
        this.$new_child.children('input[name="name"]').val('');
        if (new_name == '') return;
        var new_type = false;
        if (new_name.indexOf('#')==0) {
            new_name = new_name.slice(1).trim();
            new_type = 'topic';
        }
        var new_item = new Item({name: new_name, from_: this.model.id});
        if (new_type) new_item.set('type', new_type);
        new_item.save(null, {success: function() {
            
            self.model.get('items').add(new_item);
        }});
    },
    doShowForm: function(e) { e.preventDefault(); e.stopPropagation(); this.showForm(); },
    showForm: function() {
        this.children_view.scrollDown();
        this.$new_child.show();
        this.$new_child.children('input').focus();
    },
    hideForm: function() {
        this.$new_child.hide();
    },
});

var ItemsView = Backbone.View.extend({
    events: { 'scroll': 'showScrollers' },
    initialize: function() {
        _(this).bindAll();
        this._item_views = [];
        this.collection.each(this.add);
        this.collection.bind('add', this.add);
        this.collection.bind('remove', this.remove);
    },
    add: function(item) {
        //console.log("adding");
        var item_view = new ItemView({model: item});
        this._item_views.push(item_view);
        if (this._rendered) {
            this.$el.append(item_view.render().$el);
            this.scrollDown();
        }
    },
    remove: function(item) {
        //console.log('removing');
        var to_remove = _.find(this._item_views, function (iv) { return iv.model.get('_id') == item.get('_id'); });
        var first, last = false;
        if (_.indexOf(this._item_views, to_remove) == 0) var first = true;
        if (_.indexOf(this._item_views, to_remove) == _.size(this._item_views)-1) var last = true;
        to_remove.remove();
        this._item_views = _.without(this._item_views, to_remove);
        if (this._scrolls) {
            if (first) this.scrollUp();
            if (last) this.scrollDown();
            this.showScrollers();
        }
    },
    render: function() {
        var self = this;
        this.$el.empty();
        _(this._item_views).each(function(item_view) {
            self.$el.append(item_view.render().$el);
        });
        this._rendered = true;
        return this;
    },
    addScrollers: function() {
        this.$topScroller = $(h('div', {class: 'scroller top'})); this.$el.before(this.$topScroller);
        this.$bottomScroller = $(h('div', {class: 'scroller bottom'})); this.$el.after(this.$bottomScroller);
        this.showScrollers();
        this._scrolls = true;
    },
    showScrollers: function() {
        var c = this.$el;
        //console.log(this.$topScroller);
        //console.log(c.scrollTop() + ', ' + c.height() + ', ' + c[0].scrollHeight);
        if (c.scrollTop() > 0) { this.$topScroller.show() } else {  this.$topScroller.hide(); }
        if (c.scrollTop() + c.height() < c[0].scrollHeight - 3) { this.$bottomScroller.show() } else { this.$bottomScroller.hide(); }
    },
    scrollUp: function() {
        //console.log("going up...");
        this.$el.scrollTop(0);
        this.showScrollers();
    },
    scrollDown: function() {
        //console.log("going down...");
        this.$el.scrollTop(this.$el[0].scrollHeight - this.$el.height());
        this.showScrollers();
    },
});

var ItemsController = Backbone.Router.extend({
    routes: {
        '': 'index',
        'new': 'newItem',
        'nodes/*id': 'showItem',
    },

    initialize: function() {
        _.bindAll(this);
        this.roots = [];
        this.lastId = false;
        this.selectedNode = false;
    },

    index: function() {
        this.showItem(root_id);
    },

    newItem: function() {

    },

    showItem: function(id) {
        //console.log(id);
        id_ = id.split('/').join('__')
        var self = this;
        // Check if item already showing
        if (self.roots.indexOf(id) != -1) {
            return self.selectNode(id_);
        }
        var node = new Item({ _id: id });
        self.roots.push(id);
        // Get the node from the server and display on success
        node.fetch({ success: function(node_returned) {
            // Create a new one
            var node_view = new NodeView({model: node});
            $("#roots").append(node_view.render().el);
            // Center it
            var from_node = $('#item_'+id_).parents('.node');
            // Set it next to the parent if it exists
            if (from_node.size()) {
                node_view.$el.offset({
                    left: from_node.offset().left + from_node.width() + 25,
                    top: from_node.offset().top + from_node.height() + 25,
                });
            // Otherwise set it in the top right
            } else {
                //node_view.$el.offset({
                    //left: $(window).width()/2 - node_view.$el.width()/2,
                    //top: $(window).height()/2 - node_view.$el.height()/2,
                //});
                node_view.$el.offset({left: 50, top: 100});
            }
            // Set it up and select it
            node_view.children_view.addScrollers();
            self.selectNode(id_);
            // Make plumbing
            jsPlumb.draggable(node_view.$el, {start: function() { self.selectNode(id_); }});
            
            var e0 = jsPlumb.addEndpoint($('#item_'+id_), {container: $('#roots'), anchor: ['RightMiddle', 'LeftMiddle']})
            var e1 = jsPlumb.addEndpoint($('#node_'+id_+' .name'), {container: $('#roots'), anchor: 'Continuous'})
            jsPlumb.connect({source: e0, target: e1});
        } });
    },

    selectNode: function(id) {
        if (this.selectedNode) this.selectedNode.removeClass('selected');
        this.selectedNode = $('#node_'+id);
        this.selectedNode.addClass('selected');
        //console.log('selected?');
        //console.log(id);
        //$('.selected').removeClass('selected');
        //$('#node_'+id).addClass('selected');
    },
});

jsPlumb.ready(function() {
    //jsPlumb.setRenderMode(jsPlumb.CANVAS);
    jsPlumb.Defaults.Connector = ["Bezier", {curviness: 50}];
    jsPlumb.Defaults.DragOptions = { cursor: "pointer", zIndex:2000 };
    jsPlumb.Defaults.PaintStyle = { lineWidth:2, strokeStyle: 'rgb(200,200,200)' };
    jsPlumb.Defaults.HoverPaintStyle = { lineWidth: 3, strokeStyle: 'rgb(180,180,180)' };
    jsPlumb.Defaults.Endpoint = ["Dot", {radius: 4, fillStyle: 'rgba(200, 200, 200, 0.8)'}];
    jsPlumb.Defaults.EndpointStyle = {fillStyle: 'rgba(200, 200, 200, 0.8)'};
    jsPlumb.Defaults.Endpoints = ["Blank", "Blank"];
    //jsPlumb.draggable(jsPlumb.getSelector('.root'));
});

$(function() {
    controller = new ItemsController();
    Backbone.history.start();
    //$('#roots').draggable();
    $('#roots').width($(window).width());
    $('#roots').height($(window).height());
    $.infinitedrag('#roots', {}, {
        width: 500,
        height: 500,
        start_col: 0,
        start_row: 0,
        oncreate: function($el, col, row) {}
    });
    $(document).click(function() { $('input').blur(); $('.selected').removeClass('selected'); });
});
