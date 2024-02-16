from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename = "web_scrape_flipkart.log" , level=logging.INFO)
import pymongo
app = Flask(__name__)

@app.route("/" ,methods = ["GET"])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ["POST" , "GET"])
def func():
    if request.method == "POST":
        try:
            searchstr = request.form['content'].replace(" " , "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstr
            UClient = uReq(flipkart_url)
            flipkart_page = UClient.read()
            UClient.close()
            flipkart_html = bs(flipkart_page , 'html.parser')
            flipkart_products = flipkart_html.findAll('div' , {"class" : "_1AtVbE col-12-12"})
            del flipkart_products[0:3]
            flipkart_prod = flipkart_products[0]
            fk_prod_link = "https://www.flipkart.com" + flipkart_prod.div.div.div.a['href']
            prodRes = requests.get(fk_prod_link)
            prodRes.encoding = 'uft-8'
            prod_html = bs(prodRes.text , 'html.parser')
            print(prod_html)
            review_boxes = prod_html.find_all('div' , {"class" : "_16PBlm"})
            
            filename = searchstr + ".csv"
            fw = open(filename , 'w')
            reviews = []
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            for review_box in review_boxes:
                try:
                    name = review_box.div.div.find_all('p' ,  {"class" : "_2sc7ZR _2V5EHH"})[0].text
                except:
                    logging.info("name")
                try:
                    rating = review_box.div.div.div.div.text
                except:
                    rating = "No rating"
                    logging.info("rating")
                try:
                    commentHead = review_box.div.div.div.p.text
                except:
                    commentHead = "No comment Heading"
                    logging.info(commentHead)

                try:
                    comtag = review_box.div.div.find_all('div' , {"class" : ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)
                
                mydict = {"Product": searchstr, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            
            
            logging.info("log my final result {}".format(reviews))
            
            uri = "mongodb+srv://Akhil_Akkala:Mongodb0987@akhilak.mmn1viy.mongodb.net/?retryWrites=true&w=majority"
            # Create a new client and connect to the server
            client = pymongo.MongoClient(uri)
            db = client['flipkart_review_scrape_data']
            review_col = db['flipkart_review_scrape_data']
            review_col.insert_many(reviews)
            
            
            
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
        
    else:
        
        return render_template('index.html')
            
    

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
