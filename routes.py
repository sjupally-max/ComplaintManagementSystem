import os
from functools import wraps
from uuid import uuid4
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Complaint, Category, User
from forms import ComplaintForm

main_bp = Blueprint("main", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def store_attachment(file):
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        raise ValueError("Allowed files: PNG, JPG, GIF, PDF, DOC, DOCX.")
    filename = f"{uuid4().hex}_{secure_filename(file.filename)}"
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    return filename


def form_categories(form):
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name)]


def can_access(complaint):
    return current_user.is_admin or complaint.user_id == current_user.id


@main_bp.route("/")
@login_required
def dashboard():
    query = Complaint.query if current_user.is_admin else Complaint.query.filter_by(user_id=current_user.id)
    counts = {s: query.filter_by(status=s).count() for s in ("Pending", "In Progress", "Resolved")}
    return render_template("dashboard.html", total=sum(counts.values()), counts=counts, recent=query.order_by(Complaint.created_at.desc()).limit(5).all())


@main_bp.route("/complaints")
@login_required
def complaints():
    query = Complaint.query if current_user.is_admin else Complaint.query.filter_by(user_id=current_user.id)
    search = request.args.get("search", "").strip()
    category = request.args.get("category", type=int)
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    if search:
        pattern = f"%{search}%"
        query = query.filter(db.or_(Complaint.subject.ilike(pattern), Complaint.description.ilike(pattern), Complaint.name.ilike(pattern)))
    if category: query = query.filter_by(category_id=category)
    if status: query = query.filter_by(status=status)
    if priority: query = query.filter_by(priority=priority)
    page = query.order_by(Complaint.created_at.desc()).paginate(page=request.args.get("page", 1, type=int), per_page=8, error_out=False)
    return render_template("complaints.html", complaints=page, categories=Category.query.order_by(Category.name).all())


@main_bp.route("/complaints/add", methods=["GET", "POST"])
@login_required
def add_complaint():
    form = ComplaintForm()
    form_categories(form)
    if form.validate_on_submit():
        try:
            attachment = store_attachment(form.attachment.data)
            item = Complaint(name=form.name.data.strip(), email=form.email.data.lower(), mobile=form.mobile.data.strip(), category_id=form.category_id.data, subject=form.subject.data.strip(), description=form.description.data.strip(), priority=form.priority.data, attachment=attachment, user_id=current_user.id)
            db.session.add(item); db.session.commit()
            flash(f"Complaint #{item.id} submitted successfully.", "success")
            return redirect(url_for("main.complaints"))
        except ValueError as error:
            flash(str(error), "danger")
    return render_template("add_complaint.html", form=form)


@main_bp.route("/complaints/<int:complaint_id>/edit", methods=["GET", "POST"])
@login_required
def edit_complaint(complaint_id):
    item = db.get_or_404(Complaint, complaint_id)
    if not can_access(item): abort(403)
    form = ComplaintForm(obj=item)
    form_categories(form)
    if form.validate_on_submit():
        try:
            for field in ("name", "email", "mobile", "category_id", "subject", "description", "priority"):
                setattr(item, field, getattr(form, field).data.strip() if field in ("name", "email", "mobile", "subject", "description") else getattr(form, field).data)
            if form.attachment.data and form.attachment.data.filename:
                item.attachment = store_attachment(form.attachment.data)
            db.session.commit(); flash("Complaint updated.", "success")
            return redirect(url_for("main.complaints"))
        except ValueError as error: flash(str(error), "danger")
    return render_template("edit_complaint.html", form=form, complaint=item)


@main_bp.post("/complaints/<int:complaint_id>/delete")
@login_required
def delete_complaint(complaint_id):
    item = db.get_or_404(Complaint, complaint_id)
    if not can_access(item): abort(403)
    db.session.delete(item); db.session.commit(); flash("Complaint deleted.", "info")
    return redirect(url_for("main.complaints"))


@main_bp.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    counts = {s: Complaint.query.filter_by(status=s).count() for s in ("Pending", "In Progress", "Resolved")}
    category_data = [(c.name, len(c.complaints)) for c in Category.query.order_by(Category.name)]
    return render_template("admin_dashboard.html", total=sum(counts.values()), counts=counts, users=User.query.count(), recent=Complaint.query.order_by(Complaint.created_at.desc()).limit(7).all(), category_data=category_data)


@main_bp.post("/admin/complaints/<int:complaint_id>/status")
@login_required
@admin_required
def update_status(complaint_id):
    item = db.get_or_404(Complaint, complaint_id)
    status = request.form.get("status")
    if status in ("Pending", "In Progress", "Resolved"):
        item.status = status; db.session.commit(); flash("Status updated.", "success")
    else: flash("Invalid status.", "danger")
    return redirect(request.referrer or url_for("main.admin_dashboard"))


@main_bp.app_errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="You do not have permission to access this page."), 403


@main_bp.app_errorhandler(413)
def too_large(_error):
    flash("File is too large. Maximum size is 8 MB.", "danger")
    return redirect(request.referrer or url_for("main.complaints"))
