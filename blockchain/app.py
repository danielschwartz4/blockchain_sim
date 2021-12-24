from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
	# We run the proof of work algorithm to get the next proof...
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)

	# We must receive a reward for finding the proof.
	# The sender is "0" to signify that this node has mined a new coin.
	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1,
	)

	# Forge the new Block by adding it to the chain
	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	response = {
		'message': "New Block Forged",
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash'],
	}
	return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def transaction():
	values = request.get_json()

	# Check that the required fields are in the POST'ed data
	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
		return 'Missing values', 400

	# Create a new Transaction
	index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

	response = {'message': f'Transaction will be added to Block {index}'}
	# print(response)
	return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}
	return jsonify(response), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
	values = request.get_json()
	nodes = values['nodes']
	if nodes is None:
		return "Error: Please supply a valid list of nodes", 400

	for node in nodes:
		blockchain.register_node(node)
	response = {
							'message': 'New nodes have been added',
							'total_nodes': list(blockchain.nodes),
							}
	return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
	replaced = blockchain.resolve_conflicts()

	if replaced:
			response = {
					'message': 'Our chain was replaced',
					'new_chain': blockchain.chain
			}
	else:
			response = {
					'message': 'Our chain is authoritative',
					'chain': blockchain.chain
			}

	return jsonify(response), 200


@app.route('/psn/problem', methods=['POST'])
def problem_proposal():
	problem = request.get_json()['problem']
	if problem is None:
		return "Error: Please supply a problem", 400

	# !! TODO
	blockchain.propose_problem(problem)
	response = {
							'message': 'A new problem has been proposed',
							'problem': problem,
							}
	return response


@app.route('/psn/solution', methods=['POST'])
def solution_proposal():
	solution = request.get_json()['solution']
	if solution is None:
		return "Error: Please supply a solution", 400

	# !! TODO
	blockchain.propose_solution(solution)
	response = {
							'message': 'A new solution has been proposed',
							'problem': solution,
							}
	return response


@app.route('/psn/problem/vote', methods=['POST'])
def problem_vote():
	problem_id = request.get_json()['problem_id']
	if problem_id is None:
		return "Error: Please supply a problem_id", 400

	# !! TODO
	blockchain.vote_problem(problem_id)
	response = {
							'message': f'Problem {problem_id} ' + 'has been voted for',
							'problem': problem_id,
							}
	return response

@app.route('/psn/solution/vote', methods=['POST'])
def solution_vote():
	solution_id = request.get_json()['solution_id']
	if solution_id is None:
		return "Error: Please supply a solution_id", 400

	# !! TODO
	blockchain.vote_solutions()
	response = {
							'message': f'Problem {solution_id} ' + 'has been voted for',
							'solution': solution_id,
							}
	return response


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)