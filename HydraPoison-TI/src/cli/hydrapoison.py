# -*- coding: utf-8 -*-
import argparse
from src.pipeline.folder_pipeline import FolderPipeline

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subs-in", default="data/input/subtitles")
    ap.add_argument("--subs-out", default="data/output/subtitles_poisoned")
    ap.add_argument("--imgs-in", default="data/input/images")
    ap.add_argument("--imgs-out", default="data/output/images_poisoned")
    ap.add_argument("--epsilon", type=float, default=8/255.0)
    ap.add_argument("--target-class", type=int, default=None)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    pipe = FolderPipeline(
        subs_in=args.subs_in, subs_out=args.subs_out,
        imgs_in=args.imgs_in, imgs_out=args.imgs_out,
        epsilon=args.epsilon, target_class=args.target_class, device=args.device
    )
    pipe.run_all()

if __name__ == "__main__":
    main()
