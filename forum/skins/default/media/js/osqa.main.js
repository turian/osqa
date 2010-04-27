var response_commands = {
    update_post_score: function(id, inc) {
        var $score_board = $('#post-' + id + '-score');
        var current = parseInt($score_board.html())
        if (isNaN(current)){
            current = 0;
        }
        $score_board.html(current + inc)
    },

    update_user_post_vote: function(id, vote_type) {
        var $upvote_button = $('#post-' + id + '-upvote');
        var $downvote_button = $('#post-' + id + '-downvote');

        $upvote_button.removeClass('on');
        $downvote_button.removeClass('on');

        if (vote_type == 'up') {
            $upvote_button.addClass('on');
        } else if (vote_type == 'down') {
            $downvote_button.addClass('on');
        }
    },

    update_favorite_count: function(inc) {
        var $favorite_count = $('#favorite-count');
        var count = parseInt($favorite_count.html());

        if (isNaN(count))
            count = 0;

        count += inc;

        if (count == 0)
            count = '';

        $favorite_count.html(count);
    },

    update_favorite_mark: function(type) {
        if (type == 'on') {
            $('#favorite-mark').addClass('on');
        } else {
            $('#favorite-mark').removeClass('on');
        }
    },

    mark_accepted: function(id) {
        $('.accepted-answer').removeClass('accepted-answer');
        $('.accept-answer.on').removeClass('on');
        
        var $answer = $('#answer-container-' + id);
        $answer.addClass('accepted-answer');
        $answer.find('.accept-answer').addClass('on');
    },

    unmark_accepted: function(id) {
        var $answer = $('#answer-container-' + id);
        $answer.removeClass('accepted-answer');
        $answer.find('.accept-answer').removeClass('on');
    },

    remove_comment: function(id) {
        var $comment = $('#comment-' + id);
        $comment.css('background', 'red')
        $comment.fadeOut('slow', function() {
            $comment.remove();    
        });
    },

    insert_comment: function(post_id, comment_id, comment, username, profile_url, delete_url) {
        var $container = $('#comments-container-' + post_id);
        var skeleton = $('#new-comment-skeleton-' + post_id).html().toString();

        skeleton = skeleton.replace(new RegExp('%ID%', 'g'), comment_id)
                .replace(new RegExp('%COMMENT%', 'g'), comment)
                .replace(new RegExp('%USERNAME%', 'g'), username)
                .replace(new RegExp('%PROFILE_URL%', 'g'), profile_url)
                .replace(new RegExp('%DELETE_URL%', 'g'), delete_url);

        $container.append(skeleton);

        $('#comment-' + comment_id).slideDown('slow');
    },

    update_comment: function(comment_id, comment_text) {
        var $comment = $('#comment-' + comment_id);
        $comment.find('.comment-text').html(comment_text);

        $comment.slideDown('slow');
    },

    mark_deleted: function(post_type, post_id) {
        if (post_type == 'answer') {
            var $answer = $('#answer-container-' + post_id);
            $answer.addClass('deleted');
        } else {
            var $container = $('#question-table');
            $container.addClass('deleted');
        }
    },

    set_subscription_button: function(text) {
        $('.subscription_switch').html(text);
    },

    set_subscription_status: function(text) {
        $('.subscription-status').html(text);
    }
}

function show_message(object, msg) {
    var div = $('<div class="vote-notification"><h3>' + msg + '</h3>(' +
    'click to close' + ')</div>');

    div.click(function(event) {
        $(".vote-notification").fadeOut("fast", function() { $(this).remove(); });
    });

    object.parent().append(div);
    div.fadeIn("fast");
}

function process_ajax_response(data, el) {
    if (!data.success && data['error_message'] != undefined) {
        show_message(el, data.error_message)
    } else if (typeof data['commands'] != undefined){
        for (var command in data.commands) {
            response_commands[command].apply(null, data.commands[command])
        }

        if (data['message'] != undefined) {
            show_message(el, data.message)
        }
    }
}

$(function() {
    $('a.ajax-command').live('click', function() {
        var el = $(this);
        $.getJSON(el.attr('href'), function(data) {
            process_ajax_response(data, el);
        });

        return false
    });

    $('div.comment-form-container').each(function() {
        var $container = $(this);
        var $form = $container.find('form');
        var $textarea = $container.find('textarea');
        var $button = $container.find('input[type="submit"]');
        var $chars_left_message = $('.comment-chars-left');
        var $chars_counter = $container.find('.comments-char-left-count');

        var $comment_tools = $container.parent().find('.comment-tools');
        var $add_comment_link = $comment_tools.find('.add-comment-link');
        var $comments_container = $container.parent().find('.comments-container');

        var max_length = parseInt($chars_counter.html());
        var comment_in_form = false;

        function cleanup_form() {
            $textarea.val('');
            $chars_counter.html(max_length);
            $chars_left_message.removeClass('warn');
            comment_in_form = false;
        }

        cleanup_form();

        function calculate_chars_left() {
            var length = $textarea.val().length;
            var allow = true;

            if (length < max_length) {
                if (length < max_length * 0.75) {
                    $chars_left_message.removeClass('warn');
                } else {
                    $chars_left_message.addClass('warn');
                }
            } else {
                allow = false;
            }

            $chars_counter.html(max_length - length);
            return allow;
        }

        function show_comment_form() {
            $container.slideDown('slow');
            $add_comment_link.fadeOut('slow');
        }

        function hide_comment_form() {
            $container.slideUp('slow');
            $add_comment_link.fadeIn('slow');
        }

        $add_comment_link.click(function(){
            cleanup_form();
            show_comment_form();
            return false;
        });

        $comment_tools.find('.show-all-comments-link').click(function() {
            $comments_container.find('.not_top_scorer').slideDown('slow');
            $(this).fadeOut('slow');
            $comment_tools.find('.comments-showing').fadeOut('slow');
            return false;
        });

        $('#' + $comments_container.attr('id') + ' .comment-edit').live('click', function() {
            var $link = $(this);
            var comment_id = /comment-(\d+)-edit/.exec($link.attr('id'))[1];
            var $comment = $link.parents('.comment');
            var comment_text = $comment.find('.comment-text').text().trim();

            comment_in_form = comment_id;
            $textarea.val(comment_text);
            calculate_chars_left();
            $comment.slideUp('slow');
            show_comment_form();
            return false;
        });

        $textarea.keyup(calculate_chars_left);

        $button.click(function() {
            if ($textarea.val().length > max_length) {
                show_message($button, "Your comment exceeds the max number of characters allowed.");
            } else {
                var post_data = {
                    comment: $textarea.val()
                }

                if (comment_in_form) {
                    post_data['id'] = comment_in_form;
                }

                $.post($form.attr('action'), post_data, function(data) {
                    process_ajax_response(data, $button);
                    cleanup_form();
                }, "json")
            }

            hide_comment_form();
            return false;
        });
    });

            
});

//var scriptUrl, interestingTags, ignoredTags, tags, $;
function pickedTags(){

    var sendAjax = function(tagname, reason, action, callback){
        var url = scriptUrl;
        if (action == 'add'){
            url += $.i18n._('mark-tag/');
            if (reason == 'good'){
                url += $.i18n._('interesting/');
            }
            else {
                url += $.i18n._('ignored/');
            }
        }
        else {
            url += $.i18n._('unmark-tag/');
        }
        url = url + tagname + '/';

        var call_settings = {
            type:'POST',
            url:url
        };
        if (callback !== false){
            call_settings.success = callback;
        }
        $.ajax(call_settings);
    };


    var unpickTag = function(from_target ,tagname, reason, send_ajax){
        //send ajax request to delete tag
        var deleteTagLocally = function(){
            from_target[tagname].remove();
            delete from_target[tagname];
        };
        if (send_ajax){
            sendAjax(tagname,reason,'remove',deleteTagLocally);
        }
        else {
            deleteTagLocally();
        }

    };

    var setupTagDeleteEvents = function(obj,tag_store,tagname,reason,send_ajax){
        obj.unbind('mouseover').bind('mouseover', function(){
            $(this).attr('src', mediaUrl('media/images/close-small-hover.png'));
        });
        obj.unbind('mouseout').bind('mouseout', function(){
            $(this).attr('src', mediaUrl('media/images/close-small-dark.png'));
        });
        obj.click( function(){
            unpickTag(tag_store,tagname,reason,send_ajax);
        });
    };

    var handlePickedTag = function(obj,reason){
        var tagname = $.trim($(obj).prev().attr('value'));
        var to_target = interestingTags;
        var from_target = ignoredTags;
        var to_tag_container;
        if (reason == 'bad'){
            to_target = ignoredTags;
            from_target = interestingTags;
            to_tag_container = $('div .tags.ignored');
        }
        else if (reason != 'good'){
            return;
        }
        else {
            to_tag_container = $('div .tags.interesting');
        }

        if (tagname in from_target){
            unpickTag(from_target,tagname,reason,false);
        }

        if (!(tagname in to_target)){
            //send ajax request to pick this tag

            sendAjax(tagname,reason,'add',function(){
                var new_tag = $('<span></span>');
                new_tag.addClass('deletable-tag');
                var tag_link = $('<a></a>');
                tag_link.attr('rel','tag');
                tag_link.attr('href', scriptUrl + $.i18n._('tags/') + tagname);
                tag_link.html(tagname);
                var del_link = $('<img></img>');
                del_link.addClass('delete-icon');
                del_link.attr('src', mediaUrl('/media/images/close-small-dark.png'));

                setupTagDeleteEvents(del_link, to_target, tagname, reason, true);

                new_tag.append(tag_link);
                new_tag.append(del_link);
                to_tag_container.append(new_tag);

                to_target[tagname] = new_tag;
            });
        }
    };

    var collectPickedTags = function(){
        var good_prefix = 'interesting-tag-';
        var bad_prefix = 'ignored-tag-';
        var good_re = RegExp('^' + good_prefix);
        var bad_re = RegExp('^' + bad_prefix);
        interestingTags = {};
        ignoredTags = {};
        $('.deletable-tag').each(
            function(i,item){
                var item_id = $(item).attr('id');
                var tag_name, tag_store;
                if (good_re.test(item_id)){
                    tag_name = item_id.replace(good_prefix,'');
                    tag_store = interestingTags;
                    reason = 'good';
                }
                else if (bad_re.test(item_id)){
                    tag_name = item_id.replace(bad_prefix,'');
                    tag_store = ignoredTags;
                    reason = 'bad';
                }
                else {
                    return;
                }
                tag_store[tag_name] = $(item);
                setupTagDeleteEvents($(item).find('img'),tag_store,tag_name,reason,true);
            }
        );
    };

    var setupHideIgnoredQuestionsControl = function(){
        $('#hideIgnoredTagsCb').unbind('click').click(function(){
            $.ajax({
                        type: 'POST',
                        dataType: 'json',
                        cache: false,
                        url: scriptUrl + $.i18n._('command/'),
                        data: {command:'toggle-ignored-questions'}
                    });
        });
    };
    return {
        init: function(){
            collectPickedTags();
            setupHideIgnoredQuestionsControl();
            $("#interestingTagInput, #ignoredTagInput").autocomplete("/matching_tags", {
                minChars: 1,
                matchContains: true,
                max: 20,
                /*multiple: false, - the favorite tags and ignore tags don't let you do multiple tags
                multipleSeparator: " "*/

                formatItem: function(row, i, max, value) {
                    return row[1].split(".")[0] + " (" + row[1].split(".")[1] + ")";
                },

                formatResult: function(row, i, max, value){
                    return row[0];
                }

            });
            $("#interestingTagAdd").click(function(){handlePickedTag(this,'good');});
            $("#ignoredTagAdd").click(function(){handlePickedTag(this,'bad');});
        }
    };
}

$(document).ready( function(){
    //if (window.tags != undefined)
        pickedTags().init();
});

Hilite={elementid:"content",exact:true,max_nodes:1000,onload:true,style_name:"hilite",style_name_suffix:true,debug_referrer:""};Hilite.search_engines=[["local","q"],["cnprog\\.","q"],["google\\.","q"],["search\\.yahoo\\.","p"],["search\\.msn\\.","q"],["search\\.live\\.","query"],["search\\.aol\\.","userQuery"],["ask\\.com","q"],["altavista\\.","q"],["feedster\\.","q"],["search\\.lycos\\.","q"],["alltheweb\\.","q"],["technorati\\.com/search/([^\\?/]+)",1],["dogpile\\.com/info\\.dogpl/search/web/([^\\?/]+)",1,true]];Hilite.decodeReferrer=function(d){var g=null;var e=new RegExp("");for(var c=0;c<Hilite.search_engines.length;c++){var f=Hilite.search_engines[c];e.compile("^http://(www\\.)?"+f[0],"i");var b=d.match(e);if(b){var a;if(isNaN(f[1])){a=Hilite.decodeReferrerQS(d,f[1])}else{a=b[f[1]+1]}if(a){a=decodeURIComponent(a);if(f.length>2&&f[2]){a=decodeURIComponent(a)}a=a.replace(/\'|"/g,"");a=a.split(/[\s,\+\.]+/);return a}break}}return null};Hilite.decodeReferrerQS=function(f,d){var b=f.indexOf("?");var c;if(b>=0){var a=new String(f.substring(b+1));b=0;c=0;while((b>=0)&&((c=a.indexOf("=",b))>=0)){var e,g;e=a.substring(b,c);b=a.indexOf("&",c)+1;if(e==d){if(b<=0){return a.substring(c+1)}else{return a.substring(c+1,b-1)}}else{if(b<=0){return null}}}}return null};Hilite.hiliteElement=function(f,e){if(!e||f.childNodes.length==0){return}var c=new Array();for(var b=0;b<e.length;b++){e[b]=e[b].toLowerCase();if(Hilite.exact){c.push("\\b"+e[b]+"\\b")}else{c.push(e[b])}}c=new RegExp(c.join("|"),"i");var a={};for(var b=0;b<e.length;b++){if(Hilite.style_name_suffix){a[e[b]]=Hilite.style_name+(b+1)}else{a[e[b]]=Hilite.style_name}}var d=function(m){var j=c.exec(m.data);if(j){var n=j[0];var i="";var h=m.splitText(j.index);var g=h.splitText(n.length);var l=m.ownerDocument.createElement("SPAN");m.parentNode.replaceChild(l,h);l.className=a[n.toLowerCase()];l.appendChild(h);return l}else{return m}};Hilite.walkElements(f.childNodes[0],1,d)};Hilite.hilite=function(){var a=Hilite.debug_referrer?Hilite.debug_referrer:document.referrer;var b=null;a=Hilite.decodeReferrer(a);if(a&&((Hilite.elementid&&(b=document.getElementById(Hilite.elementid)))||(b=document.body))){Hilite.hiliteElement(b,a)}};Hilite.walkElements=function(d,f,e){var a=/^(script|style|textarea)/i;var c=0;while(d&&f>0){c++;if(c>=Hilite.max_nodes){var b=function(){Hilite.walkElements(d,f,e)};setTimeout(b,50);return}if(d.nodeType==1){if(!a.test(d.tagName)&&d.childNodes.length>0){d=d.childNodes[0];f++;continue}}else{if(d.nodeType==3){d=e(d)}}if(d.nextSibling){d=d.nextSibling}else{while(f>0){d=d.parentNode;f--;if(d.nextSibling){d=d.nextSibling;break}}}}};if(Hilite.onload){if(window.attachEvent){window.attachEvent("onload",Hilite.hilite)}else{if(window.addEventListener){window.addEventListener("load",Hilite.hilite,false)}else{var __onload=window.onload;window.onload=function(){Hilite.hilite();__onload()}}}};

var mediaUrl = function(resource){
    return scriptUrl + 'm/' + osqaSkin + '/' + resource;
};

/*
 * jQuery i18n plugin
 * @requires jQuery v1.1 or later
 *
 * Examples at: http://recurser.com/articles/2008/02/21/jquery-i18n-translation-plugin/
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Based on 'javascript i18n that almost doesn't suck' by markos
 * http://markos.gaivo.net/blog/?p=100
 *
 * Revision: $Id$
 * Version: 1.0.0  Feb-10-2008
 */
 (function($) {
/**
 * i18n provides a mechanism for translating strings using a jscript dictionary.
 *
 */


/*
 * i18n property list
 */
$.i18n = {

/**
 * setDictionary()
 * Initialise the dictionary and translate nodes
 *
 * @param property_list i18n_dict : The dictionary to use for translation
 */
	setDictionary: function(i18n_dict) {
		i18n_dict = i18n_dict;
	},

/**
 * _()
 * The actual translation function. Looks the given string up in the
 * dictionary and returns the translation if one exists. If a translation
 * is not found, returns the original word
 *
 * @param string str : The string to translate
 * @param property_list params : params for using printf() on the string
 * @return string : Translated word
 *
 */
	_: function (str, params) {
		var transl = str;
		if (i18n_dict&& i18n_dict[str]) {
			transl = i18n_dict[str];
		}
		return this.printf(transl, params);
	},

/**
 * toEntity()
 * Change non-ASCII characters to entity representation
 *
 * @param string str : The string to transform
 * @return string result : Original string with non-ASCII content converted to entities
 *
 */
	toEntity: function (str) {
		var result = '';
		for (var i=0;i<str.length; i++) {
			if (str.charCodeAt(i) > 128)
				result += "&#"+str.charCodeAt(i)+";";
			else
				result += str.charAt(i);
		}
		return result;
	},

/**
 * stripStr()
 *
 * @param string str : The string to strip
 * @return string result : Stripped string
 *
 */
 	stripStr: function(str) {
		return str.replace(/^\s*/, "").replace(/\s*$/, "");
	},

/**
 * stripStrML()
 *
 * @param string str : The multi-line string to strip
 * @return string result : Stripped string
 *
 */
	stripStrML: function(str) {
		// Split because m flag doesn't exist before JS1.5 and we need to
		// strip newlines anyway
		var parts = str.split('\n');
		for (var i=0; i<parts.length; i++)
			parts[i] = stripStr(parts[i]);

		// Don't join with empty strings, because it "concats" words
		// And strip again
		return stripStr(parts.join(" "));
	},

/*
 * printf()
 * C-printf like function, which substitutes %s with parameters
 * given in list. %%s is used to escape %s.
 *
 * Doesn't work in IE5.0 (splice)
 *
 * @param string S : string to perform printf on.
 * @param string L : Array of arguments for printf()
 */
	printf: function(S, L) {
		if (!L) return S;

		var nS = "";
		var tS = S.split("%s");

		for(var i=0; i<L.length; i++) {
			if (tS[i].lastIndexOf('%') == tS[i].length-1 && i != L.length-1)
				tS[i] += "s"+tS.splice(i+1,1)[0];
			nS += tS[i] + L[i];
		}
		return nS + tS[tS.length-1];
	}

};


})(jQuery);


//var i18nLang;
var i18nZh = {
	'insufficient privilege':'??????????',
	'cannot pick own answer as best':'??????????????',
	'anonymous users cannot select favorite questions':'?????????????',
	'please login':'??????',
	'anonymous users cannot vote':'????????',
	'>15 points requried to upvote':'??+15?????????',
	'>100 points required to downvote':'??+100?????????',
	'please see': '??',
	'cannot vote for own posts':'??????????',
	'daily vote cap exhausted':'????????????????',
	'cannot revoke old vote':'??????????????',
	'please confirm offensive':"??????????????????????",
	'anonymous users cannot flag offensive posts':'???????????',
	'cannot flag message as offensive twice':'???????',
	'flag offensive cap exhausted':'?????????????5?‘??’???',
	'need >15 points to report spam':"??+15??????‘???’?",
	'confirm delete':"?????/????????",
	'anonymous users cannot delete/undelete':"???????????????",
	'post recovered':"?????????????",
	'post deleted':"????????????",
	'add comment':'????',
	'community karma points':'????',
	'to comment, need':'????',
	'delete this comment':'?????',
	'hide comments':"????",
	'add a comment':"????",
	'comments':"??",
	'confirm delete comment':"?????????",
	'characters':'??',
	'can write':'???',
	'click to close':'???????',
	'loading...':'???...',
	'tags cannot be empty':'???????',
	'tablimits info':"??5????????????20????",
	'content cannot be empty':'???????',
	'content minchars': '????? {0} ???',
	'please enter title':'??????',
	'title minchars':"????? {0} ???",
	'delete':'??',
	'undelete':	'??',
	'bold':'??',
	'italic':'??',
	'link':'???',
	'quote':'??',
	'preformatted text':'??',
	'image':'??',
	'numbered list':'??????',
	'bulleted list':'??????',
	'heading':'??',
	'horizontal bar':'???',
	'undo':'??',
	'redo':'??',
	'enter image url':'<b>??????</b></p><p>???<br />http://www.example.com/image.jpg   \"????\"',
	'enter url':'<b>??Web??</b></p><p>???<br />http://www.cnprog.com/   \"????\"</p>"',
	'upload image':'?????????'
};

var i18nEn = {
	'need >15 points to report spam':'need >15 points to report spam ',
    '>15 points requried to upvote':'>15 points required to upvote ',
	'tags cannot be empty':'please enter at least one tag',
	'anonymous users cannot vote':'sorry, anonymous users cannot vote ',
	'anonymous users cannot select favorite questions':'sorry, anonymous users cannot select favorite questions ',
	'to comment, need': '(to comment other people\'s posts, karma ',
	'please see':'please see ',
	'community karma points':' or more is necessary) - ',
	'upload image':'Upload image:',
	'enter image url':'enter URL of the image, e.g. http://www.example.com/image.jpg \"image title\"',
	'enter url':'enter Web address, e.g. http://www.example.com \"page title\"',
	'daily vote cap exhausted':'sorry, you\'ve used up todays vote cap',
	'cannot pick own answer as best':'sorry, you cannot accept your own answer',
	'cannot revoke old vote':'sorry, older votes cannot be revoked',
	'please confirm offensive':'are you sure this post is offensive, contains spam, advertising, malicious remarks, etc.?',
	'flag offensive cap exhausted':'sorry, you\'ve used up todays cap of flagging offensive messages ',
	'confirm delete':'are you sure you want to delete this?',
	'anonymous users cannot delete/undelete':'sorry, anonymous users cannot delete or undelete posts',
	'post recovered':'your post is now restored!',
	'post deleted':'your post has been deleted',
	'confirm delete comment':'do you really want to delete this comment?',
	'can write':'have ',
	'tablimits info':'up to 5 tags, no more than 20 characters each',
	'content minchars': 'please enter more than {0} characters',
	'title minchars':"please enter at least {0} characters",
	'characters':'characters left',
    'cannot vote for own posts':'sorry, you cannot vote for your own posts',
    'cannot flag message as offensive twice':'cannot flag message as offensive twice ',
	'>100 points required to downvote':'>100 points required to downvote '
};

var i18nEs = {
	'insufficient privilege':'privilegio insuficiente',
	'cannot pick own answer as best':'no puede escoger su propia respuesta como la mejor',
	'anonymous users cannot select favorite questions':'usuarios anonimos no pueden seleccionar',
	'please login':'por favor inicie sesión',
	'anonymous users cannot vote':'usuarios anónimos no pueden votar',
	'>15 points requried to upvote': '>15 puntos requeridos para votar positivamente',
	'>100 points required to downvote':'>100 puntos requeridos para votar negativamente',
	'please see': 'por favor vea',
	'cannot vote for own posts':'no se puede votar por sus propias publicaciones',
	'daily vote cap exhausted':'cuota de votos diarios excedida',
	'cannot revoke old vote':'no puede revocar un voto viejo',
	'please confirm offensive':"por favor confirme ofensiva",
	'anonymous users cannot flag offensive posts':'usuarios anónimos no pueden marcar publicaciones como ofensivas',
	'cannot flag message as offensive twice':'no puede marcar mensaje como ofensivo dos veces',
	'flag offensive cap exhausted':'cuota para marcar ofensivas ha sido excedida',
	'need >15 points to report spam':"necesita >15 puntos para reportar spam",
	'confirm delete':"¿Está seguro que desea borrar esto?",
	'anonymous users cannot delete/undelete':"usuarios anónimos no pueden borrar o recuperar publicaciones",
	'post recovered':"publicación recuperada",
	'post deleted':"publicación borrada?",
	'add comment':'agregar comentario',
	'community karma points':'reputación comunitaria',
	'to comment, need':'para comentar, necesita reputación',
	'delete this comment':'borrar este comentario',
	'hide comments':"ocultar comentarios",
	'add a comment':"agregar comentarios",
	'comments':"comentarios",
	'confirm delete comment':"¿Realmente desea borrar este comentario?",
	'characters':'caracteres faltantes',
	'can write':'tiene ',
	'click to close':'haga click para cerrar',
	'loading...':'cargando...',
	'tags cannot be empty':'las etiquetas no pueden estar vacías',
	'tablimits info':"hasta 5 etiquetas de no mas de 20 caracteres cada una",
	'content cannot be empty':'el contenido no puede estar vacío',
	'content minchars': 'por favor introduzca mas de {0} caracteres',
	'please enter title':'por favor ingrese un título',
	'title minchars':"por favor introduzca al menos {0} caracteres",
	'delete':'borrar',
	'undelete':	'recuperar',
	'bold': 'negrita',
	'italic':'cursiva',
	'link':'enlace',
	'quote':'citar',
	'preformatted text':'texto preformateado',
	'image':'imagen',
	'numbered list':'lista numerada',
	'bulleted list':'lista no numerada',
	'heading':'??',
	'horizontal bar':'barra horizontal',
	'undo':'deshacer',
	'redo':'rehacer',
	'enter image url':'introduzca la URL de la imagen, por ejemplo?<br />http://www.example.com/image.jpg   \"titulo de imagen\"',
	'enter url':'introduzca direcciones web, ejemplo?<br />http://www.cnprog.com/   \"titulo del enlace\"</p>"',
	'upload image':'cargar imagen?',
	'questions/' : 'preguntas/',
	'vote/' : 'votar/'
};

var i18n = {
	'en':i18nEn,
	'zh_CN':i18nZh,
	'es':i18nEs
};

var i18n_dict = i18n[i18nLang];

/*
	jQuery TextAreaResizer plugin
	Created on 17th January 2008 by Ryan O'Dell
	Version 1.0.4
*/(function($){var textarea,staticOffset;var iLastMousePos=0;var iMin=32;var grip;$.fn.TextAreaResizer=function(){return this.each(function(){textarea=$(this).addClass('processed'),staticOffset=null;$(this).wrap('<div class="resizable-textarea"><span></span></div>').parent().append($('<div class="grippie"></div>').bind("mousedown",{el:this},startDrag));var grippie=$('div.grippie',$(this).parent())[0];grippie.style.marginRight=(grippie.offsetWidth-$(this)[0].offsetWidth)+'px'})};function startDrag(e){textarea=$(e.data.el);textarea.blur();iLastMousePos=mousePosition(e).y;staticOffset=textarea.height()-iLastMousePos;textarea.css('opacity',0.25);$(document).mousemove(performDrag).mouseup(endDrag);return false}function performDrag(e){var iThisMousePos=mousePosition(e).y;var iMousePos=staticOffset+iThisMousePos;if(iLastMousePos>=(iThisMousePos)){iMousePos-=5}iLastMousePos=iThisMousePos;iMousePos=Math.max(iMin,iMousePos);textarea.height(iMousePos+'px');if(iMousePos<iMin){endDrag(e)}return false}function endDrag(e){$(document).unbind('mousemove',performDrag).unbind('mouseup',endDrag);textarea.css('opacity',1);textarea.focus();textarea=null;staticOffset=null;iLastMousePos=0}function mousePosition(e){return{x:e.clientX+document.documentElement.scrollLeft,y:e.clientY+document.documentElement.scrollTop}}})(jQuery);
/*
 * Autocomplete - jQuery plugin 1.0.2
 * Copyright (c) 2007 Dylan Verheul, Dan G. Switzer, Anjesh Tuladhar, Jörn Zaefferer
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 */;(function($){$.fn.extend({autocomplete:function(urlOrData,options){var isUrl=typeof urlOrData=="string";options=$.extend({},$.Autocompleter.defaults,{url:isUrl?urlOrData:null,data:isUrl?null:urlOrData,delay:isUrl?$.Autocompleter.defaults.delay:10,max:options&&!options.scroll?10:150},options);options.highlight=options.highlight||function(value){return value;};options.formatMatch=options.formatMatch||options.formatItem;return this.each(function(){new $.Autocompleter(this,options);});},result:function(handler){return this.bind("result",handler);},search:function(handler){return this.trigger("search",[handler]);},flushCache:function(){return this.trigger("flushCache");},setOptions:function(options){return this.trigger("setOptions",[options]);},unautocomplete:function(){return this.trigger("unautocomplete");}});$.Autocompleter=function(input,options){var KEY={UP:38,DOWN:40,DEL:46,TAB:9,RETURN:13,ESC:27,COMMA:188,PAGEUP:33,PAGEDOWN:34,BACKSPACE:8};var $input=$(input).attr("autocomplete","off").addClass(options.inputClass);var timeout;var previousValue="";var cache=$.Autocompleter.Cache(options);var hasFocus=0;var lastKeyPressCode;var config={mouseDownOnSelect:false};var select=$.Autocompleter.Select(options,input,selectCurrent,config);var blockSubmit;$.browser.opera&&$(input.form).bind("submit.autocomplete",function(){if(blockSubmit){blockSubmit=false;return false;}});$input.bind(($.browser.opera?"keypress":"keydown")+".autocomplete",function(event){lastKeyPressCode=event.keyCode;switch(event.keyCode){case KEY.UP:event.preventDefault();if(select.visible()){select.prev();}else{onChange(0,true);}break;case KEY.DOWN:event.preventDefault();if(select.visible()){select.next();}else{onChange(0,true);}break;case KEY.PAGEUP:event.preventDefault();if(select.visible()){select.pageUp();}else{onChange(0,true);}break;case KEY.PAGEDOWN:event.preventDefault();if(select.visible()){select.pageDown();}else{onChange(0,true);}break;case options.multiple&&$.trim(options.multipleSeparator)==","&&KEY.COMMA:case KEY.TAB:case KEY.RETURN:if(selectCurrent()){event.preventDefault();blockSubmit=true;return false;}break;case KEY.ESC:select.hide();break;default:clearTimeout(timeout);timeout=setTimeout(onChange,options.delay);break;}}).focus(function(){hasFocus++;}).blur(function(){hasFocus=0;if(!config.mouseDownOnSelect){hideResults();}}).click(function(){if(hasFocus++>1&&!select.visible()){onChange(0,true);}}).bind("search",function(){var fn=(arguments.length>1)?arguments[1]:null;function findValueCallback(q,data){var result;if(data&&data.length){for(var i=0;i<data.length;i++){if(data[i].result.toLowerCase()==q.toLowerCase()){result=data[i];break;}}}if(typeof fn=="function")fn(result);else $input.trigger("result",result&&[result.data,result.value]);}$.each(trimWords($input.val()),function(i,value){request(value,findValueCallback,findValueCallback);});}).bind("flushCache",function(){cache.flush();}).bind("setOptions",function(){$.extend(options,arguments[1]);if("data"in arguments[1])cache.populate();}).bind("unautocomplete",function(){select.unbind();$input.unbind();$(input.form).unbind(".autocomplete");});function selectCurrent(){var selected=select.selected();if(!selected)return false;var v=selected.result;previousValue=v;if(options.multiple){var words=trimWords($input.val());if(words.length>1){v=words.slice(0,words.length-1).join(options.multipleSeparator)+options.multipleSeparator+v;}v+=options.multipleSeparator;}$input.val(v);hideResultsNow();$input.trigger("result",[selected.data,selected.value]);return true;}function onChange(crap,skipPrevCheck){if(lastKeyPressCode==KEY.DEL){select.hide();return;}var currentValue=$input.val();if(!skipPrevCheck&&currentValue==previousValue)return;previousValue=currentValue;currentValue=lastWord(currentValue);if(currentValue.length>=options.minChars){$input.addClass(options.loadingClass);if(!options.matchCase)currentValue=currentValue.toLowerCase();request(currentValue,receiveData,hideResultsNow);}else{stopLoading();select.hide();}};function trimWords(value){if(!value){return[""];}var words=value.split(options.multipleSeparator);var result=[];$.each(words,function(i,value){if($.trim(value))result[i]=$.trim(value);});return result;}function lastWord(value){if(!options.multiple)return value;var words=trimWords(value);return words[words.length-1];}function autoFill(q,sValue){if(options.autoFill&&(lastWord($input.val()).toLowerCase()==q.toLowerCase())&&lastKeyPressCode!=KEY.BACKSPACE){$input.val($input.val()+sValue.substring(lastWord(previousValue).length));$.Autocompleter.Selection(input,previousValue.length,previousValue.length+sValue.length);}};function hideResults(){clearTimeout(timeout);timeout=setTimeout(hideResultsNow,200);};function hideResultsNow(){var wasVisible=select.visible();select.hide();clearTimeout(timeout);stopLoading();if(options.mustMatch){$input.search(function(result){if(!result){if(options.multiple){var words=trimWords($input.val()).slice(0,-1);$input.val(words.join(options.multipleSeparator)+(words.length?options.multipleSeparator:""));}else
    $input.val("");}});}if(wasVisible)$.Autocompleter.Selection(input,input.value.length,input.value.length);};function receiveData(q,data){if(data&&data.length&&hasFocus){stopLoading();select.display(data,q);autoFill(q,data[0].value);select.show();}else{hideResultsNow();}};function request(term,success,failure){if(!options.matchCase)term=term.toLowerCase();var data=cache.load(term);if(data&&data.length){success(term,data);}else if((typeof options.url=="string")&&(options.url.length>0)){var extraParams={timestamp:+new Date()};$.each(options.extraParams,function(key,param){extraParams[key]=typeof param=="function"?param():param;});$.ajax({mode:"abort",port:"autocomplete"+input.name,dataType:options.dataType,url:options.url,data:$.extend({q:lastWord(term),limit:options.max},extraParams),success:function(data){var parsed=options.parse&&options.parse(data)||parse(data);cache.add(term,parsed);success(term,parsed);}});}else{select.emptyList();failure(term);}};function parse(data){var parsed=[];var rows=data.split("\n");for(var i=0;i<rows.length;i++){var row=$.trim(rows[i]);if(row){row=row.split("|");parsed[parsed.length]={data:row,value:row[0],result:options.formatResult&&options.formatResult(row,row[0])||row[0]};}}return parsed;};function stopLoading(){$input.removeClass(options.loadingClass);};};$.Autocompleter.defaults={inputClass:"ac_input",resultsClass:"ac_results",loadingClass:"ac_loading",minChars:1,delay:400,matchCase:false,matchSubset:true,matchContains:false,cacheLength:10,max:100,mustMatch:false,extraParams:{},selectFirst:true,formatItem:function(row){return row[0];},formatMatch:null,autoFill:false,width:0,multiple:false,multipleSeparator:", ",highlight:function(value,term){return value.replace(new RegExp("(?![^&;]+;)(?!<[^<>]*)("+term.replace(/([\^\$\(\)\[\]\{\}\*\.\+\?\|\\])/gi,"\\$1")+")(?![^<>]*>)(?![^&;]+;)","gi"),"<strong>$1</strong>");},scroll:true,scrollHeight:180};$.Autocompleter.Cache=function(options){var data={};var length=0;function matchSubset(s,sub){if(!options.matchCase)s=s.toLowerCase();var i=s.indexOf(sub);if(i==-1)return false;return i==0||options.matchContains;};function add(q,value){if(length>options.cacheLength){flush();}if(!data[q]){length++;}data[q]=value;}function populate(){if(!options.data)return false;var stMatchSets={},nullData=0;if(!options.url)options.cacheLength=1;stMatchSets[""]=[];for(var i=0,ol=options.data.length;i<ol;i++){var rawValue=options.data[i];rawValue=(typeof rawValue=="string")?[rawValue]:rawValue;var value=options.formatMatch(rawValue,i+1,options.data.length);if(value===false)continue;var firstChar=value.charAt(0).toLowerCase();if(!stMatchSets[firstChar])stMatchSets[firstChar]=[];var row={value:value,data:rawValue,result:options.formatResult&&options.formatResult(rawValue)||value};stMatchSets[firstChar].push(row);if(nullData++<options.max){stMatchSets[""].push(row);}};$.each(stMatchSets,function(i,value){options.cacheLength++;add(i,value);});}setTimeout(populate,25);function flush(){data={};length=0;}return{flush:flush,add:add,populate:populate,load:function(q){if(!options.cacheLength||!length)return null;if(!options.url&&options.matchContains){var csub=[];for(var k in data){if(k.length>0){var c=data[k];$.each(c,function(i,x){if(matchSubset(x.value,q)){csub.push(x);}});}}return csub;}else
    if(data[q]){return data[q];}else
    if(options.matchSubset){for(var i=q.length-1;i>=options.minChars;i--){var c=data[q.substr(0,i)];if(c){var csub=[];$.each(c,function(i,x){if(matchSubset(x.value,q)){csub[csub.length]=x;}});return csub;}}}return null;}};};$.Autocompleter.Select=function(options,input,select,config){var CLASSES={ACTIVE:"ac_over"};var listItems,active=-1,data,term="",needsInit=true,element,list;function init(){if(!needsInit)return;element=$("<div/>").hide().addClass(options.resultsClass).css("position","absolute").appendTo(document.body);list=$("<ul/>").appendTo(element).mouseover(function(event){if(target(event).nodeName&&target(event).nodeName.toUpperCase()=='LI'){active=$("li",list).removeClass(CLASSES.ACTIVE).index(target(event));$(target(event)).addClass(CLASSES.ACTIVE);}}).click(function(event){$(target(event)).addClass(CLASSES.ACTIVE);select();input.focus();return false;}).mousedown(function(){config.mouseDownOnSelect=true;}).mouseup(function(){config.mouseDownOnSelect=false;});if(options.width>0)element.css("width",options.width);needsInit=false;}function target(event){var element=event.target;while(element&&element.tagName!="LI")element=element.parentNode;if(!element)return[];return element;}function moveSelect(step){listItems.slice(active,active+1).removeClass(CLASSES.ACTIVE);movePosition(step);var activeItem=listItems.slice(active,active+1).addClass(CLASSES.ACTIVE);if(options.scroll){var offset=0;listItems.slice(0,active).each(function(){offset+=this.offsetHeight;});if((offset+activeItem[0].offsetHeight-list.scrollTop())>list[0].clientHeight){list.scrollTop(offset+activeItem[0].offsetHeight-list.innerHeight());}else if(offset<list.scrollTop()){list.scrollTop(offset);}}};function movePosition(step){active+=step;if(active<0){active=listItems.size()-1;}else if(active>=listItems.size()){active=0;}}function limitNumberOfItems(available){return options.max&&options.max<available?options.max:available;}function fillList(){list.empty();var max=limitNumberOfItems(data.length);for(var i=0;i<max;i++){if(!data[i])continue;var formatted=options.formatItem(data[i].data,i+1,max,data[i].value,term);if(formatted===false)continue;var li=$("<li/>").html(options.highlight(formatted,term)).addClass(i%2==0?"ac_even":"ac_odd").appendTo(list)[0];$.data(li,"ac_data",data[i]);}listItems=list.find("li");if(options.selectFirst){listItems.slice(0,1).addClass(CLASSES.ACTIVE);active=0;}if($.fn.bgiframe)list.bgiframe();}return{display:function(d,q){init();data=d;term=q;fillList();},next:function(){moveSelect(1);},prev:function(){moveSelect(-1);},pageUp:function(){if(active!=0&&active-8<0){moveSelect(-active);}else{moveSelect(-8);}},pageDown:function(){if(active!=listItems.size()-1&&active+8>listItems.size()){moveSelect(listItems.size()-1-active);}else{moveSelect(8);}},hide:function(){element&&element.hide();listItems&&listItems.removeClass(CLASSES.ACTIVE);active=-1;},visible:function(){return element&&element.is(":visible");},current:function(){return this.visible()&&(listItems.filter("."+CLASSES.ACTIVE)[0]||options.selectFirst&&listItems[0]);},show:function(){var offset=$(input).offset();element.css({width:typeof options.width=="string"||options.width>0?options.width:$(input).width(),top:offset.top+input.offsetHeight,left:offset.left}).show();if(options.scroll){list.scrollTop(0);list.css({maxHeight:options.scrollHeight,overflow:'auto'});if($.browser.msie&&typeof document.body.style.maxHeight==="undefined"){var listHeight=0;listItems.each(function(){listHeight+=this.offsetHeight;});var scrollbarsVisible=listHeight>options.scrollHeight;list.css('height',scrollbarsVisible?options.scrollHeight:listHeight);if(!scrollbarsVisible){listItems.width(list.width()-parseInt(listItems.css("padding-left"))-parseInt(listItems.css("padding-right")));}}}},selected:function(){var selected=listItems&&listItems.filter("."+CLASSES.ACTIVE).removeClass(CLASSES.ACTIVE);return selected&&selected.length&&$.data(selected[0],"ac_data");},emptyList:function(){list&&list.empty();},unbind:function(){element&&element.remove();}};};$.Autocompleter.Selection=function(field,start,end){if(field.createTextRange){var selRange=field.createTextRange();selRange.collapse(true);selRange.moveStart("character",start);selRange.moveEnd("character",end);selRange.select();}else if(field.setSelectionRange){field.setSelectionRange(start,end);}else{if(field.selectionStart){field.selectionStart=start;field.selectionEnd=end;}}field.focus();};})(jQuery);

var notify = function() {
    var visible = false;
    return {
        show: function(html) {
            if (html) {
                $("body").css("margin-top", "2.2em");
                $(".notify span").html(html);
            }
            $(".notify").fadeIn("slow");
            visible = true;
        },
        close: function(doPostback) {
            if (doPostback) {
               $.post(scriptUrl + $.i18n._("messages/") +
                $.i18n._("markread/"), { formdata: "required" });
            }
            $(".notify").fadeOut("fast");
            $("body").css("margin-top", "0");
            visible = false;
        },
        isVisible: function() { return visible; }
    };
} ();