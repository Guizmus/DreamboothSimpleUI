@echo off
cls

call git init -q data/diffusers/SD-2.0-512
cd data/diffusers/SD-2.0-512
call git lfs install
call git remote add -f origin https://huggingface.co/stabilityai/stable-diffusion-2-base
call git config core.sparseCheckout true
echo scheduler/ >> .git/info/sparse-checkout
echo text_encoder/ >> .git/info/sparse-checkout
echo tokenizer/ >> .git/info/sparse-checkout
echo unet/ >> .git/info/sparse-checkout
echo vae/ >> .git/info/sparse-checkout
echo model_index.json >> .git/info/sparse-checkout
call git pull -q origin main
cd ../../..

echo Diffusers for SD-2.0-512 installed