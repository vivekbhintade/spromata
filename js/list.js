var root;
var selectedNode;

var Item = Backbone.Model.extend({
    url: function() { 
        if (this.get('id'))
            return "/" + this.get('id');
        else
            return "/new";
    },
    initialize: function() {
        //if (!this.get('id')) this.set({'id': this.get('_id')['$oid']});
        if (!this.get('id')) this.set({'id': this.get('_id')});
        if (!this.get('items')) this.set({'items': new Items()});
        else this.set({'items': new Items(this.get('items'))});
    },
    parse: function(response) {
        //response['id'] = response['_id']['$oid'];
        response['id'] = response['_id'];
        response['items'] = new Items(response['items']);
        return response;
    },
});

var Items = Backbone.Collection.extend({
    model: Item,
});

var ItemView = Backbone.View.extend({
    events: {
        'dblclick': 'grow',
        'click': 'select',
        'submit form': 'addChild',
    },
    initialize: function(options) {
        _.bindAll(this);
        this.el = h(
            'div',
            {class: 'item', id: this.model.get('id')},
            [
                h('div', {class: 'content'}, [
                    h('div', {class: 'name'}),
                ]),
                h('div', {class: 'attributes'}),
                h('div', {class: 'items'}),
            ]
        );
        this.form = h('form', {action: this.model.url() + '/add'},
            [h('input', {type: 'text', name: 'name'})]);
        this.$el = $(this.el);
        this.$form = $(this.form);
        this.$form.appendTo(this.$el);
        this.model.bind('change', this.render, this);
        this.model.bind('destroy', this.remove, this);
        if (options.parent) this.parent = options.parent;
        this.children = [];
    },
    addItem: function(new_item) {
        var new_item_view = new ItemView({model: new_item, parent: this});
        this.children.push(new_item_view);
        this.$(".items").first().append(new_item_view.render().el);
    },
    render: function() {
        var self = this;
        if (this.model.get('items').length) {
            this.$el.addClass('expandable');
            this.expandable = true;
        } else {
            this.expandable = false;
        }
        var name = this.model.get('name');
        var name_rep;
        if (['.png','.jpg','.gif'].indexOf(name.substr(-4)) != -1) name_rep = h('img', {src: name});
        else if (name.substr(0,7) == 'http://') name_rep = h('a', {href: name}, name);
        else name_rep = h('span', name);
        this.$(".name").first().empty().append(name_rep);
        this.$(".attributes").first().empty();
        this.$(".items").first().empty();
        this.$form.children('input[name="name"]').bind('keydown', 'esc', function() {
            this.blur();
            self.hideForm();
        });
        this.children = [];
        _.each(this.model.get('items').models, function(new_item) {
            self.addItem(new_item);
        });
        return this;
    },
    addChild: function(e) {
        e.preventDefault();
        e.stopPropagation();
        //var url = $(e.target).attr('action');
        //this.model.set({url: url})
        //this.model.save()
        //$.post(url, {name: $(e.target).children('input[name="name"]').val()});
        var new_name = this.$form.children('input[name="name"]').val();
        var new_item = new Item({name: new_name, from_:this.model.id});
        new_item.save();
        this.model.get('items').add(new_item);
        this.render();
        this.expand();
        this.$form.children('input[name="name"]').val('');
        this.$form.children('input[name="name"]').blur();
        this.hideForm();
    },
    expand: function() {
        if (!this.grown) {
            this.model.fetch();
            this.grown = true;
        }
        $(this.el).addClass('expanded');
        this.expanded = true;
    },
    unexpand: function() {
        $(this.el).removeClass('expanded');
        this.expanded = false;
    },
    grow: function(e) {
        console.log('grow');
        e.stopPropagation();
        e.preventDefault();
        if ($(this.el).hasClass('expanded')) {
            this.unexpand();
        } else {
            this.expand();
        }
    },
    showForm: function() {
        if (!$(this.el).hasClass('expanded')) 
            this.expand();
        $(this.el).children('form').first().show();
        $(this.el).children('form').first().children('input').focus();
    },
    hideForm: function() {
        this.$('form').hide();
    },
    select: function(e) {
        e.stopPropagation();
        e.preventDefault();
        select_node(this);
    },
    update: function() {
        this.model.fetch();
    },
    clear: function() {
        this.model.destroy();
    },
    remove: function() {
        this.parent.children = _.without(this.parent.children, this);
        $(this.el).remove();
    },
});

function select_node(node_view) {
    selectedNode.hideForm();
    $('.selected').removeClass('selected');
    $(node_view.el).addClass('selected');
    selectedNode = node_view;
    console.log(selectedNode)
}

function move_left() {
    if (selectedNode.expanded) selectedNode.unexpand();
    else select_node(selectedNode.parent);
}
function move_down(go_inner) {
    go_inner = typeof go_inner !== 'undefined' ? go_inner : true;
    if (selectedNode.expanded && go_inner) {
        move_right();
    } else {
        var select_pos = selectedNode.parent.children.indexOf(selectedNode);
        if ((select_pos + 1) < selectedNode.parent.children.length) {
            select_node(selectedNode.parent.children[select_pos + 1]);
        } else {
            select_node(selectedNode.parent);
            move_down(false);
        }
    }
}
function find_deepest_child(from_node) {
    if (from_node.expanded) {
        return find_deepest_child(_.last(from_node.children));
    } else { return from_node; }
}
function find_up_node(from_node) {
    var select_pos = from_node.parent.children.indexOf(from_node);
    if ((select_pos) > 0) {
        var up_node = from_node.parent.children[select_pos - 1];
        return find_deepest_child(up_node);
    } else { return from_node.parent; }
}
function move_up() {
    var select_pos = selectedNode.parent.children.indexOf(selectedNode);
    select_node(find_up_node(selectedNode));
}
function move_right() {
    if (selectedNode.expandable) {
        if (!selectedNode.expanded) selectedNode.expand();
        else select_node(selectedNode.children[0]);
    }
}
function new_node(e) {
    e.preventDefault();
    e.stopPropagation();
    console.log('newing');
    console.log(selectedNode);
    selectedNode.showForm();
}

$(function() {
    $(document).bind('keydown', 'h', move_left);
    $(document).bind('keydown', 'j', move_down);
    $(document).bind('keydown', 'k', move_up);
    $(document).bind('keydown', 'l', move_right);
    $(document).bind('keydown', 'o', new_node);
    $(document).bind('keydown', 'backspace', function(e) {
        if (!$('input:focus').length) {
            e.preventDefault();
            e.stopPropagation();
            var up_node = find_up_node(selectedNode);
            selectedNode.clear();
            select_node(up_node);
            selectedNode.update();
        }
    });
});


