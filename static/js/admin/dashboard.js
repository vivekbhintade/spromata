User = Backbone.Model.extend({ });
Users = Backbone.Collection.extend({
    model: User,
    url: '/admin/users',
});

Product = Backbone.Model.extend({ });
Products = Backbone.Collection.extend({
    model: Product,
    url: '/admin/products',
});

UserModalView = Backbone.View.extend({
    events: {
        'click .save': 'save',
    },
    initialize: function(options) {
        _.bindAll(this);
        if (options.el) this.el = options.el;
        else this.el = $('#modal__user_' + this.model.id);
        this.$el = $(this.el);
        this.$title_name = this.$('span.name');
        this.$form = this.$('form');
        this.$input_name = this.$('input[name=name]');
        this.$input_email = this.$('input[name=email]');
        this.$input_type = this.$('input[name=type]');
        this.$checkbox_verified = this.$('input[name=verified]');
        this.delegateEvents();
        this.model.bind('change', this.render);
    },
    render: function() {
        this.$title_name.text(this.model.get('name'));
        this.$input_name.val(this.model.get('name'));
        this.$input_email.val(this.model.get('email'));
        this.$input_type.val(this.model.get('type'));
        if (this.model.get('verified')) this.$checkbox_verified.attr('checked', true);
        else this.$checkbox_verified.attr('checked', false);
    },
    save: function(e) {
        e.stopPropagation();
        e.preventDefault();
        this.model.save({
            name: this.$input_name.val(),
            email: this.$input_email.val(),
            type: this.$input_type.val(),
            verified: this.$checkbox_verified.attr('checked') ? true : false,
        });
        this.hide();
    },
    show: function() {
        this.$el.modal('show');
    },
    hide: function() {
        this.$el.modal('hide');
    },
});

ProductModalView = Backbone.View.extend({
    events: {
        'click .save': 'save',
    },
    initialize: function(options) {
        _.bindAll(this);
        if (options.el) this.el = options.el;
        else this.el = $('#modal__product_' + this.model.id);
        this.$el = $(this.el);
        this.$title_name = this.$('span.name');
        this.$form = this.$('form');
        this.$input_name = this.$('input[name=name]');
        this.$input_category = this.$('input[name=category]');
        this.$input_weight = this.$('input[name=weight]');
        this.delegateEvents();
        this.model.bind('change', this.render);
    },
    render: function() {
        this.$title_name.text(this.model.get('name'));
        this.$input_name.val(this.model.get('name'));
        this.$input_category.val(this.model.get('category'));
        this.$input_weight.val(this.model.get('weight'));
    },
    save: function(e) {
        e.stopPropagation();
        e.preventDefault();
        this.model.save({
            name: this.$input_name.val(),
            category: this.$input_category.val(),
            weight: this.$input_weight.val(),
        });
        this.hide();
    },
    show: function() {
        this.$el.modal('show');
    },
    hide: function() {
        this.$el.modal('hide');
    },
});

UserRowView = Backbone.View.extend({
    events: {
        'click .user_name': 'showModal',
        'click .user_select input[type=checkbox]': 'setSelected'
    },
    initialize: function(options) {
        _.bindAll(this);
        if (options.el) this.el = options.el;
        else this.el = $('#tr__user_' + this.model.id);
        this.$el = $(this.el);
        this.$checkbox = this.$('.user_select input[type=checkbox]');
        this.$td_name = this.$('.user_name');
        this.$td_email = this.$('.user_email');
        this.$td_type = this.$('.user_type');
        this.$td_verified = this.$('.user_verified');
        this.model.bind('change', this.render);
        this.delegateEvents();
    },
    render: function() {
        this.$td_name.text(this.model.get('name'));
        this.$td_email.text(this.model.get('email'));
        this.$td_type.text(this.model.get('type'));
        this.$td_verified.html('<i class="icon-'+ this.model.get('verified') +'"></i>');
        this.delegateEvents();
    },
    showModal: function() {
        console.log('show modal');
        $('#modal__user_'+this.model.id).modal('show');
    },
    setSelected: function() {
        console.log('do something with select');
        if (this.$checkbox.attr('checked')) {
            this.$el.addClass('selected');
        } else {
            this.$el.removeClass('selected');
        }
    },
});

ProductRowView = Backbone.View.extend({
    events: {
        'click .product_name': 'showModal',
        'click .product_select input[type=checkbox]': 'setSelected'
    },
    initialize: function(options) {
        _.bindAll(this);
        if (options.el) this.el = options.el;
        else this.el = $('#tr__product_' + this.model.id);
        this.$el = $(this.el);
        this.$checkbox = this.$('.product_select input[type=checkbox]');
        this.$td_name = this.$('.product_name');
        this.$td_preview = this.$('.product_preview');
        this.$td_category = this.$('.product_category');
        this.$td_weight = this.$('.product_weight');
        this.model.bind('change', this.render);
        this.delegateEvents();
    },
    render: function() {
        this.$td_name.text(this.model.get('name'));
        this.$td_preview.find('img').attr({src: this.model.get('preview')});
        this.$td_category.text(this.model.get('category'));
        this.$td_weight.text(this.model.get('weight'));
        this.delegateEvents();
    },
    showModal: function() {
        console.log('show modal?');
        $('#modal__product_'+this.model.id).modal('show');
    },
    setSelected: function() {
        console.log('do something with select');
        if (this.$checkbox.attr('checked')) {
            this.$el.addClass('selected');
        } else {
            this.$el.removeClass('selected');
        }
    },
});

ProductsTableView = Backbone.View.extend({
    initialize: function(options) {
        _.bindAll(this);
        this.collection.bind('add', this.add);
    },
    add: function(product) {
        var new_row_el = $(h('tr', {class: 'tr_product', id: 'tr__product_' + product.id}, [
            h('td', {class: 'product_select'}, h('input', {type:'checkbox'})),
            h('td', {class: 'product_preview'}, h('img')),
            h('td', {class: 'product_name'}),
            h('td', {class: 'product_vendor'}),
            h('td', {class: 'product_category'}),
            h('td', {class: 'product_weight'}),
            h('td', {class: 'product_approved'}),
        ]));
        console.log(new_row_el);
        $(this.el).find('tbody').append(new_row_el);
        var productRowView = new ProductRowView({model: product, el: new_row_el});
        productRowView.render();
        productRows[productRowView.$el.attr('id')] = productRowView;
    },
});

var userModals = {};
var userRows = {};
var productModals = {};
var productRows = {};

$(function() {
    _.each(users_json, function(user_json) {
        var user = new User(user_json);
        //users.push(user);
        users.add(user);
        var userModalView = new UserModalView({model: user});
        var userRowView = new UserRowView({model: user});
        userModals[userModalView.$el.attr('id')] = userModalView;
        userRows[userRowView.$el.attr('id')] = userRowView;
    });

    _.each(products_json, function(products_json) {
        var product = new Product(products_json);
        //products.push(product);
        products.add(product);
        var productModalView = new ProductModalView({model: product});
        var productRowView = new ProductRowView({model: product});
        productModals[productModalView.$el.attr('id')] = productModalView;
        productRows[productRowView.$el.attr('id')] = productRowView;
    });

    productsTableView = new ProductsTableView({collection: products, el: $('#products_table')});

    $('#select_all_users').click(function() {
        if ($(this).attr('checked')) {
            _.each($("tr.tr_user"), function(tr_user) {
                if ($(tr_user).is(':hidden')) return false;
                var userRow = userRows[$(tr_user).attr('id')];
                userRow.$checkbox.attr('checked', true);
                userRow.setSelected();
            });
        } else {
            _.each($("tr.tr_user"), function(tr_user) {
                if ($(tr_user).is(':hidden')) return false;
                var userRow = userRows[$(tr_user).attr('id')];
                userRow.$checkbox.attr('checked', false);
                userRow.setSelected();
            });
        }
    });

    $('#users_verify').click(function() {
        _.each($('.tr_user.selected'), function(tr_user) {
            if ($(tr_user).is(':hidden')) return false;
            var userRow = userRows[$(tr_user).attr('id')];
            var user = userRow.model;
            console.log(user.get('verified'));
            if (user.get('verified')!=true) {
                user.save({verified: true});
            }
        });
    });

    $('#users_filter_all').click(function() {
        _.each($('.tr_user'), function(tr_user) {
            $(tr_user).show();
        });
    });
    $('#users_filter_admin').click(function() {
        _.each($('.tr_user'), function(tr_user) {
            var userRow = userRows[$(tr_user).attr('id')];
            var user = userRow.model;
            if (user.get('type')=='admin') {
                userRow.$el.show();
            } else {
                userRow.$el.hide();
            }
        });
    });
    $('#users_filter_unverified').click(function() {
        _.each($('.tr_user'), function(tr_user) {
            var userRow = userRows[$(tr_user).attr('id')];
            var user = userRow.model;
            if (!user.get('verified')) {
                userRow.$el.show();
            } else {
                userRow.$el.hide();
            }
        });
    });

    $("form#add_product").submit(function(e) {
        e.preventDefault();
        productForm = $('form#add_product');
        productName = productForm.find('input[name=name]');
        products.create({
            name: productName.val(),
        });
        productName.val('');
    });
});

