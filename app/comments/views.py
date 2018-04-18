from datetime import datetime

from flask import redirect, url_for, render_template, abort, flash
from flask_login import current_user, login_required

from . import comments, forms
from .. import db, models, cache
from ..main.views import create_temp_user


def anonymous_warning():
    if not current_user.is_authenticated:
        flash(
            "You are currently not logged in. Any comments you make will publicly display your IP address. \
            Log in or sign up to hide it.",
            "danger")


@comments.route("/<page_type>/<int:page_id>/comments/", methods=["GET", "POST"])
@cache.cached()
def list_all(page_type: str, page_id: int):
    anonymous_warning()
    if "categories" == page_type:
        cls = models.Category
    elif "tools" == page_type:
        cls = models.Tool
    else:
        abort(404)

    page = cls.query.get_or_404(page_id)

    form = forms.CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            author = create_temp_user()
        else:
            author = current_user

        if form.parent_comment_id.data == "":
            parent_comment_id = None
        else:
            parent_comment_id = form.parent_comment_id.data

        comment = models.Comment(
            body=form.body.data,
            author=author,
            parent_comment_id=parent_comment_id
        )

        if "categories" == page_type:
            comment.parent_category_page_id = page.id
        elif "tools" == page_type:
            comment.parent_tool_page_id = page.id

        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('.list_all', page_type=page_type, page_id=page_id))

    comments = page.comments.filter_by(parent_comment=None)
    return render_template("comments/comments.html",
                           comments=comments,
                           page_type=page_type,
                           page=page,
                           form=form)


@comments.route("/<page_type>/<int:page_id>/comments/<int:comment_id>")
@comments.route("/<page_type>/<int:page_id>/comments/<int:comment_id>/")
def show_single(page_type: str, page_id: int, comment_id: int):
    if "categories" == page_type:
        cls = models.Category
        comment = models.Comment.query.filter_by(id=comment_id, parent_category_page_id=page_id).first_or_404()
    elif "tools" == page_type:
        cls = models.Tool
        comment = models.Comment.query.filter_by(id=comment_id, parent_tool_page_id=page_id).first_or_404()
    else:
        abort(404)

    page = cls.query.get_or_404(page_id)
    return render_template("comments/comment.html",
                           comment=comment,
                           page=page,
                           page_type=page_type)


@login_required
@comments.route("/<page_type>/<int:page_id>/comments/<int:comment_id>/delete")
def delete(page_type: str, page_id: int, comment_id: int):
    if "categories" == page_type:
        cls = models.Category
        comment = models.Comment.query.filter_by(id=comment_id, parent_category_page_id=page_id).first_or_404()
    elif "tools" == page_type:
        cls = models.Tool
        comment = models.Comment.query.filter_by(id=comment_id, parent_tool_page_id=page_id).first_or_404()
    else:
        abort(404)

    if comment.author != current_user:
        abort(403)

    comment.body = "deleted"
    comment.deleted = datetime.utcnow()
    db.session.commit()

    return redirect(url_for(".list_all", page_type=page_type, page_id=page_id))


@login_required
@comments.route("/<page_type>/<int:page_id>/comments/<int:comment_id>/edit", methods=["GET", "POST"])
def edit(page_type: str, page_id: int, comment_id: int):
    anonymous_warning()
    if "categories" == page_type:
        cls = models.Category
        comment = models.Comment.query.filter_by(id=comment_id, parent_category_page_id=page_id).first_or_404()
        page = comment.parent_category_page
    elif "tools" == page_type:
        cls = models.Tool
        comment = models.Comment.query.filter_by(id=comment_id, parent_tool_page_id=page_id).first_or_404()
        page = comment.parent_tool_page
    else:
        abort(404)

    if comment.author != current_user:
        abort(401)

    form = forms.CommentForm()
    if form.validate_on_submit():
        comment.body = form.body.data
        comment.edit_time = datetime.utcnow()

        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('.list_all', page_type=page_type, page_id=page_id))

    form.body.data = comment.body

    return render_template("comments/edit_comment.html",
                           form=form,
                           comment=comment,
                           page_type=page_type,
                           page=page)


@comments.route("/<page_type>/<int:page_id>/comments/<int:comment_id>/reply",
                methods=["GET", "POST"])
def reply(page_type: str, page_id: int, comment_id: int):
    anonymous_warning()
    if "categories" == page_type:
        cls = models.Category
    elif "tools" == page_type:
        cls = models.Tool
    else:
        abort(404)

    page = cls.query.get_or_404(page_id)
    comment = models.Comment.query.get_or_404(comment_id)

    form = forms.CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            author = create_temp_user()
        else:
            author = current_user

        comment = models.Comment(
            body=form.body.data,
            author=author,
            parent_comment_id=form.parent_comment_id.data
        )

        if "categories" == page_type:
            comment.parent_category_page_id = page.id
        elif "tools" == page_type:
            comment.parent_tool_page_id = page.id

        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('.list_all', page_type=page_type, page_id=page_id))

    form.parent_comment_id.data = comment.id
    return render_template("comments/reply.html",
                           comment=comment,
                           page=page,
                           page_type=page_type,
                           form=form)
