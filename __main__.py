from app import app
from views import main_blueprint

# register the blueprints
app.register_blueprint(main_blueprint)

# run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # app.run()
