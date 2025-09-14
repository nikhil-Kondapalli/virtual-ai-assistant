import { Live2DCubismModel } from "live2d-renderer-lite";

const MODEL_PATH = "/models/mao_pro/runtime/";
const MODEL_JSON_FILE = "mao_pro.model3.json";

export class Live2DManager {
  private container: HTMLElement | null = null;
  private canvas: HTMLCanvasElement | null = null;
  private isInitialized = false;
  private model: Live2DCubismModel | null = null;
  private analyserNode: AnalyserNode | null = null;
  private lipSyncAnimationId: number | null = null;
  private expressionIntervalId: number | null = null;

  constructor() {}

  async initialize(
    container: HTMLElement,
    analyserNode?: AnalyserNode
  ): Promise<void> {
    if (this.isInitialized) return;
    this.container = container;
    this.analyserNode = analyserNode || null;

    try {
      this.setupCanvas();
      await this.loadModel();

      this.isInitialized = true;
      console.log("Live2D Manager Initialized with live2d-renderer-lite");
    } catch (error) {
      console.error("Error initializing Live2D manager:", error);
      throw error;
    }
  }

  private setupCanvas(): void {
    this.canvas = document.createElement("canvas");
    this.canvas.width = this.container!.clientWidth;
    this.canvas.height = this.container!.clientHeight;
    this.container!.appendChild(this.canvas);
  }

  private async loadModel(): Promise<void> {
    this.model = new Live2DCubismModel(this.canvas!, {
      autoAnimate: true,
      autoInteraction: true,
      tapInteraction: true,
      randomMotion: true,
      keepAspect: false,
      checkMocConsistency: true,
      premultipliedAlpha: true,
      lipsyncSmoothing: 0.3,
      volume: 1,
      speed: 1,
      scale: 1,
      x: 0,
      y: 0,
    });

    await this.model.load(`${MODEL_PATH}${MODEL_JSON_FILE}`);
  }

  public resize(width: number, height: number): void {
    if (!this.canvas || !this.model) return;

    this.canvas.width = width;
    this.canvas.height = height;
    this.model.resize();
  }

  private lipSync = () => {
    if (!this.analyserNode || !this.model) {
      return;
    }

    const dataArray = new Uint8Array(this.analyserNode.frequencyBinCount);
    this.analyserNode.getByteFrequencyData(dataArray);

    let sum = 0;
    for (const amplitude of dataArray) {
      sum += amplitude * amplitude;
    }
    const volume = Math.sqrt(sum / dataArray.length) / 128.0;

    this.model.setParameter("ParamA", volume);

    this.lipSyncAnimationId = requestAnimationFrame(this.lipSync);
  };

  public startTalking(): void {
    if (this.lipSyncAnimationId === null) {
      this.lipSync();
    }
    if (this.expressionIntervalId === null && this.model) {
      this.expressionIntervalId = window.setInterval(() => {
        if (this.model) {
          this.model.setRandomExpression();
        }
      }, 5000);
    }
  }

  public stopTalking(): void {
    if (this.lipSyncAnimationId !== null) {
      cancelAnimationFrame(this.lipSyncAnimationId);
      this.lipSyncAnimationId = null;
    }
    if (this.expressionIntervalId !== null) {
      clearInterval(this.expressionIntervalId);
      this.expressionIntervalId = null;
    }
    if (this.model) {
      this.model.setParameter("ParamA", 0);
      this.model.expressionManager.stopAllMotions();
    }
  }

  public playAnimation(animationName: string): void {
    if (!this.model) return;
    console.log(`Playing animation: ${animationName}`);
    this.model.startMotion(animationName, 0, 3);
  }

  public setExpression(expressionName: string): void {
    if (!this.model) {
      console.log("SetExpression: Model not ready");
      return;
    }
    console.log(`Setting expression: ${expressionName}`);
    const expressions = this.model.getExpressions();
    if (expressions.includes(expressionName)) {
      this.model.setExpression(expressionName);
    } else {
      console.warn(
        `Expression "${expressionName}" not found. Available expressions: `,
        expressions
      );
    }
  }

  public destroy(): void {
    if (this.lipSyncAnimationId !== null) {
      cancelAnimationFrame(this.lipSyncAnimationId);
    }
    if (this.expressionIntervalId !== null) {
      clearInterval(this.expressionIntervalId);
    }
    if (this.model) {
      this.model.destroy(true);
      this.model = null;
    }
    if (this.canvas && this.container) {
      this.container.removeChild(this.canvas);
    }
    this.isInitialized = false;
  }

  public getModel(): any {
    return this.model;
  }

  public isReady(): boolean {
    return this.isInitialized && this.model !== null;
  }
}
