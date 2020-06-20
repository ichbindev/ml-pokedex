to train the model:
    `python train.py --dataset dataset --model pokedex.model --labelbin lb.pickle`
    
to classify a photo:
    `python classify.py --model pokedex.model --labelbin lb.pickle --image examples/char.png`

to convert the model for coreml:
    `python coremlconverter.py --model pokedex.model --labelbin lb.pickle`
    
dataset must be provided, assumed folder structure is /dataset/<label>/<images>