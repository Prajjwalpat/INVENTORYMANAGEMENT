from flask import Blueprint, request,jsonify
from pymongo.errors import DuplicateKeyError

#app = Flask(__name__)
from db import collection
from auth import authkey
from logger import logger

# client=MongoClient(mongo_uri)
# db=client['dbtest']
# collection=db['inventory']

# r1=collection.insert_one({"item":"Mango","qty":47,"price":80})
# print(f"inserted record id: {r1.inserted_id}")

#@app.route('/records', methods=['POST'])
bp=Blueprint('routes',__name__)

@bp.errorhandler(400)
def bad_request(e):
    logger.error(f"400 bad request: {e}")
    return jsonify({'error':'Bad request','message':str(e)}),400

@bp.errorhandler(404)
def not_found(e):
    logger.error(f"404 not fpund: {e}")
    return jsonify({'error':'not found','message':str(e)}),404

@bp.errorhandler(500)
def internal_error(e):
    logger.error(f"500 Internal server error: {e}")
    return jsonify({'error':'Internal server error','message':str(e)}),500

@bp.route("/inventory", methods=["POST"])
@authkey
def create_inventory():
    try:
        data=request.get_json()
        if not data or not all(k in data for k in ("item","quantity","price")):
            logger.warning("POST /inventory -invalid data provided")
            return jsonify({"error": "Invalid data. Plz provide: item,quantity,price"}),400
        result=collection.insert_one({
            "item":data["item"],
            "qty":data["quantity"],
            "price":data["price"]
        })
        logger.info(f"inventory record added for iteam: {data['item']}, id :{result.inserted_id}")
        return jsonify({"msg":"Added in inventory", "item": data['item']}),201
    except DuplicateKeyError:
        logger.warning(f"POST /inventory - Duplicate item: {data['item']}")
        return jsonify({"error":f"item {data['item']} already exists"}),409
    except Exception as e:
        logger.exception("Error in create inventory")
        return jsonify({"error":"failed to add item", "message":str(e)}),500
    
@bp.route("/inventory/<item>", methods=["GET"])
@authkey
def get_inventory(item):
    try:
        record=collection.find_one({"item":item})
        if record:
            record["_id"]=str(record["_id"])
            logger.info(f"fetched item stock: {item}")
            return jsonify(record),200

        logger.info(f"Item not found: {item}")
        return jsonify({"error":f"item not foun"}),404
    
    except Exception as e:
        logger.exception("Error in get inventory")
        return jsonify({"error":"failed to fetch item", "message":str(e)}),500
    

@bp.route("/inventory/<item>", methods=["PUT"])
@authkey
def update_inventory(item):
    try:
        data=request.get_json()
        if not data or not any(k in data for k in("quantity","price")):
            logger.warning("PUT /inventory/<item> -no data data provided")
            return jsonify({"error": "no data data provided. Plz provide: item,quantity,price"}),400
        update_fields={}
        if "quantity" in data:
            update_fields["qty"]=data["quantity"]
        if "price" in data:
            update_fields["price"]=data["price"]
        result=collection.update_one({"item":item},{"$set":update_fields})
        if result.matched_count:
            logger.info(f"Updated record for {item}")
            return jsonify({"msg":"Item updated", "item":item}), 200
        logger.info(f"Item not found: {item}")
        return jsonify({"error":"Item not found"}),404
    
    except Exception as e:
        logger.exception("Error in update inventory")
        return jsonify({"error":"failed to update item", "message":str(e)}),500
    
@bp.route("/inventory/<item>", methods=["DELETE"])
@authkey
def delete_inventory(item):
    try:
        record=collection.delete_one({"item":item})
        if record.deleted_count:
            logger.info(f"deleted item record: {item}")
            return jsonify({"msg":"record deleted", "item":item}),200

        logger.info(f"Item not found: {item}")
        return jsonify({"error":"item not foun"}),404
    
    except Exception as e:
        logger.exception("Error in delete inventory")
        return jsonify({"error":"failed to delete item", "message":str(e)}),500
    
@bp.route("/inventory", methods=["GET"])
@authkey
def list_inventory():
    try:
        items=[]
        for record in collection.find():
            record["_id"]=str(record["_id"])
            items.append(record)
        logger.info(f"Fetched all record in inventory")
        return jsonify(items),200
    
    except Exception as e:
        logger.exception("Error in fethcing inventory")
        return jsonify({"error":"failed to fetch inventory", "message":str(e)}),500
    
@bp.errorhandler(Exception)
def handle_unexpected_error(e):
    logger.exception("unhandled exception")
    return jsonify({'error':'Unexpected error','message':str(e)}),500
