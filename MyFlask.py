from flask import Flask, render_template, request, send_from_directory
import os
import work
app = Flask(__name__)


@app.route("/")
def begin():
    return render_template("begin.html")


@app.route("/visitor/")
def visitor():
    return render_template("visitor.html", status="游客模式")


@app.route("/login/", methods=["POST"])
def login():
    uid = request.form.get("uid")
    pwd = request.form.get("pwd")
    if uid == "uid" and pwd == "pwd":
        return render_template("admin.html", status="管理员模式")
    else:
        return render_template("begin.html")


def allow_file(filename):
    allow_list = ["pdf", "docx", "txt"]
    suffix = filename.split('.')
    return len(suffix) > 1 and suffix[1] in allow_list


def upload(f, op, obj, res_word):
    if not f:
        result = "上传失败"
    else:
        if not allow_file(f.filename):
            result = "类型错误"
        elif os.path.isfile(op+"_join/"+f.filename.split('.')[0]+".txt"):
            result = "同名文件"
        else:
            f.save(os.path.join(op+'/', f.filename))
            result = res_word+"成功"
            work.get_file(op)
            work.upd_mid()
    return render_template(obj, status=result)


def download(filename, obj):
    if not os.path.isfile("report/" + filename):
        return render_template(obj, status="查无此报告")
    else:
        return send_from_directory("report/", filename.encode("utf-8").decode("utf-8"), as_attachment=True)


@app.route("/admin/check_upload/", methods=["POST"])
def admin_check_upload():
    f = request.files["file"]
    return upload(f, "check", "admin.html", "检测")


@app.route("/admin/download/", methods=["POST"])
def admin_download():
    filename = request.form.get("file")+".txt"
    return download(filename, "admin.html")


@app.route("/admin/input_upload/", methods=["POST"])
def admin_input_upload():
    f = request.files["file"]
    return upload(f, "input", "admin.html", "注册")


@app.route("/admin/reset/", methods=["POST"])
def admin_reset():
    pwd = request.form.get("pwd")
    if pwd == "rst":
        work.del_mid()
        result = "重置成功"
    else:
        result = "密码错误"
    return render_template("admin.html", status=result)


@app.route("/visitor/check_upload/", methods=["POST"])
def visitor_check_upload():
    f = request.files["file"]
    return upload(f, "check", "visitor.html", "检测")


@app.route("/visitor/download/", methods=["POST"])
def visitor_download():
    filename = request.form.get("file")+".txt"
    return download(filename, "visitor.html")


if __name__ == "__main__":
    work.init()
    app.run()
