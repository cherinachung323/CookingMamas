from flask import render_template, url_for, request, redirect, session
from application.dataAccess import get_recipe_by_id, get_dietary_types, get_allergy_types, get_tool_names, \
    get_ingredient_names, get_unit_types, get_recipe_title, get_cuisine_types, get_duration, filter_by_dietary, \
    get_random_recipes, get_diet_req

from application import app
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pa$$w0rd",  # use for windows
    # password="",  # use for mac
    database="recipedb"
)

cursor = db.cursor()


@app.route('/')
@app.route('/home')
def home():
    randomrec = get_random_recipes()
    return render_template('home.html', title='Home', randomrec=randomrec)


@app.route('/about/<name>')
@app.route('/about')
def about(name):
    return render_template('about.html', name=name.capitalize(), title='About')


@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipes = get_recipe_by_id(recipe_id)
    randomrec = get_random_recipes()
    return render_template('recipe.html', recipe=recipes, randomrec=randomrec, title='Recipe')


# TO DO Create the route that will help populate the options for the database form
# Also to submit the data to the database - stored procedure?
@app.template_filter('format_timedelta')
def format_timedelta_filter(value):
    if value is None:
        return ''

    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)


@app.route('/submitrecipepage1', methods=['GET', 'POST'])
def submitrecipepage1():
    # uses the function in data access to get the list of dietary types and assigns to variable dietary type
    cuisinetype = get_cuisine_types()
    durationdata = get_duration()
    if request.method == 'POST':
        # Get data from page 1 form and store in session
        recipename = request.form['recipeName']
        recipedescription = request.form['recipeDescription']
        cuisinetype = ','.join(request.form.getlist('cuisine'))  # Convert list to comma-separated string
        preptime = request.form['prepTime']
        cooktime = request.form['cookTime']
        servingsize = request.form['serving']
        args = (recipename, recipedescription, cuisinetype, preptime, cooktime, servingsize)
        try:
            cursor.callproc('insert_recipe_v1', args)
            db.commit()

        except mysql.connector.Error as err:
            print("Error calling stored procedure: {}".format(err))
        return redirect(url_for('submitrecipepage2'))
    return render_template('submitRecipepage1.html', title='Submit', cuisinetype=cuisinetype, durationdata=durationdata)


# submitting the data to the database for each page
@app.route('/submitrecipepage2', methods=['GET', 'POST'])
def submitrecipepage2():
    # uses the function in data access to get the list of dietary types and assigns to variable dietary type
    dietarytype = get_dietary_types()
    allergytype = get_allergy_types()
    toolname = get_tool_names()
    if request.method == 'POST':
        dietarytype = ','.join(request.form.getlist('dietary'))
        allergytype = ','.join(request.form.getlist('allergy'))
        toolname = ','.join(request.form.getlist('tool'))  # Convert list to comma-separated string
        print(dietarytype, allergytype, toolname)
        cursor.callproc('insert_dietary_v1', (dietarytype,))
        db.commit()
        cursor.callproc('insert_allergy_v1', (allergytype,))
        db.commit()
        cursor.callproc('insert_tool_v1', (toolname,))
        db.commit()
        cursor.callproc('insert_image_v1', ())
        db.commit()
        return redirect(url_for('submitrecipepage3'))
    return render_template('submitRecipepage2.html', title='Submit', dietarytype=dietarytype, allergytype=allergytype,
                           toolname=toolname)


# page 3 for ingredients
# not currently displaying the ingredients once supposedly added
# got myself all confused by the sessions so between 3 and add recipe needs more thought
@app.route('/submitrecipepage3', methods=['GET', 'POST'])
def submitrecipepage3():
    ingredientname = get_ingredient_names()
    unitname = get_unit_types()
    if request.method == 'POST':
        # creating an empty list that the data from the rows can be put into to be sent to the stored procedure
        args_list = []
        # looping over all the ingredients rows created to get their data to send to the stored procedure
        for i in range(0, 11):
            ingredient_key = f'ingredientname{i}'
            quantity_key = f'quantity{i}'
            unit_key = f'unitname{i}'

            ingredient_name = request.form.get(ingredient_key)
            quantity = request.form.get(quantity_key)
            unit_name = request.form.get(unit_key)
            # because not all the rows on the form will necessarily have data - checking if they do have data
            if ingredient_name and quantity and unit_name:
                args = (ingredient_name, quantity, unit_name)
                args_list.append(args)
                print(args_list)
        # Insert data into the database
        for args in args_list:
            cursor.callproc('insert_ingredients_v1', args)
            db.commit()
        return redirect(url_for('submitrecipepage4'))
    return render_template('submitRecipepage3.html', title='Submit', ingredientname=ingredientname, unitname=unitname)


# page 4 for steps
@app.route('/submitrecipepage4', methods=['GET', 'POST'])
def submitrecipepage4():
    # uses the function in data access to get the list of dietary types and assigns to variable dietary type
    if request.method == 'POST':
        stepnumber = request.form['stepnumber']
        stepdescription = request.form['stepdescription']
        args = (stepnumber, stepdescription)
        print(args)
        # Call the stored procedure for each step number and description pair
        cursor.callproc('insert_steps_v1', args)
        db.commit()
        # this is iterated on in the javascript
        num_rows = int(request.form.get('num_rows', 0))

        # Iterate over each row and process step number and description
        for i in range(2, num_rows + 1):
            step_number_key = f'row_{i}_stepnumber'
            step_description_key = f'row_{i}_stepdescription'
            print(step_number_key, step_description_key)
            # Extract step number and description from the form data
            step_number = request.form.get(step_number_key)
            step_description = request.form.get(step_description_key)
            print(step_number, step_description)
            # Call the stored procedure with the step number and description
            args = (step_number, step_description)
            cursor.callproc('insert_steps_v1', args)
            db.commit()
        return redirect(url_for('successsubmit'))
    return render_template('submitRecipepage4.html', title='Submit')


@app.route('/submitsuccess')
def successsubmit():
    sql = """SELECT MAX(recipeID) FROM recipe;"""
    cursor.execute(sql)
    recipeid = [row[0] for row in cursor.fetchall()]
    return render_template('submitRecipeSuccess.html', title='Success', recipeid=recipeid)


@app.route('/allrecipes', methods=['GET', 'POST'])
def allrecipes():
    recipename = get_recipe_title()
    ingredientname = get_ingredient_names()
    dietarytype = get_dietary_types()

    return render_template('allrecipes.html', title='All Recipes', recipename=recipename, ingredientname=ingredientname,
                           dietarytype=dietarytype)


@app.route('/submitsuccess')
def success_submit():
    return render_template('submitRecipeSuccess.html', title='Success')


@app.route('/recipe')
def recipe_landing():
    return render_template('recipeLanding.html')


# TODO: Add dietary types - hardcode - copy this but change the dietary type
@app.route('/glutenfree')
def glutenfree():
    dietarytype = filter_by_dietary('Gluten free')
    return render_template('glutenfree.html', dietarytype=dietarytype, title='Gluten Free')


@app.route('/vegan')
def vegan():
    dietarytype = filter_by_dietary('Vegan')
    return render_template('vegan.html', dietarytype=dietarytype, title='Vegan')


@app.route('/vegetarian')
def vegetarian():
    dietarytype = filter_by_dietary('Vegetarian')
    return render_template('vegetarian.html', dietarytype=dietarytype, title='Vegetarian')


@app.route('/halal')
def halal():
    dietarytype = filter_by_dietary('Halal')
    return render_template('halal.html', dietarytype=dietarytype, title='Halal')


@app.route('/pescatarian')
def pescatarian():
    dietarytype = filter_by_dietary('Pescatarian')
    return render_template('pescatarian.html', dietarytype=dietarytype, title='Pescatarian')


@app.errorhandler(404)
def page_not_found(error):
    randomrec = get_random_recipes()
    return render_template('error404.html', randomrec=randomrec)
